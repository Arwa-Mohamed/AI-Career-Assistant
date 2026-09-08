import re

from rest_framework import generics
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cvs.models import CV
from job_matching.models import JobAnalysis

from skill_gap.services.skill_gap_service import (
    calculate_skill_gap,
)
from skill_gap.services.roadmap import (
    generate_learning_roadmap,
)

from .models import (
    InterviewAnswer,
    InterviewQuestion,
    InterviewSession,
)
from .services.interview_ai import (
    evaluate_answer,
    generate_interview_questions,
)


class StartInterviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cv_id = request.data.get("cv_id")
        job_analysis_id = request.data.get(
            "job_analysis_id"
        )
        role = request.data.get(
            "role",
            ""
        ).strip()

        if not cv_id:
            return Response(
                {"detail": "cv_id is required."},
                status=400,
            )

        if not role:
            return Response(
                {"detail": "role is required."},
                status=400,
            )

        try:
            cv = CV.objects.get(
                id=cv_id,
                user=request.user,
            )
        except CV.DoesNotExist:
            return Response(
                {"detail": "CV not found."},
                status=404,
            )

        job_analysis = None
        job_description = ""

        if job_analysis_id:
            try:
                job_analysis = JobAnalysis.objects.get(
                    id=job_analysis_id,
                    user=request.user,
                )

                job_description = (
                    job_analysis.job_description
                )

            except JobAnalysis.DoesNotExist:
                return Response(
                    {
                        "detail":
                        "Job analysis not found."
                    },
                    status=404,
                )

        current_skills = cv.parsed_data.get(
            "skills",
            []
        )

        missing_skills = []

        if job_analysis:
            gap = calculate_skill_gap(
                current_skills,
                job_analysis.required_skills,
            )

            missing_skills = gap[
                "missing_skills"
            ]

        session = InterviewSession.objects.create(
            user=request.user,
            cv=cv,
            job_analysis=job_analysis,
            role=role,
        )

        raw_questions = generate_interview_questions(
            cv_text=cv.extracted_text,
            cv_data=cv.parsed_data,
            job_description=job_description,
            role=role,
            missing_skills=missing_skills,
        )

        lines = [
            line.strip()
            for line in raw_questions.splitlines()
            if line.strip()
        ]

        questions = []

        for index, question_text in enumerate(
            lines[:5],
            start=1,
        ):
            question = InterviewQuestion.objects.create(
                session=session,
                question_text=question_text,
                category="technical",
                order=index,
            )

            questions.append({
                "id": question.id,
                "question": question.question_text,
                "order": question.order,
            })

        return Response({
            "session_id": session.id,
            "role": session.role,
            "questions": questions,
        })
        
class SubmitAnswerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, question_id):
        answer_text = request.data.get(
            "answer",
            ""
        ).strip()

        if not answer_text:
            return Response(
                {"detail": "answer is required."},
                status=400,
            )

        try:
            question = InterviewQuestion.objects.get(
                id=question_id,
                session__user=request.user,
            )
        except InterviewQuestion.DoesNotExist:
            return Response(
                {"detail": "Question not found."},
                status=404,
            )

        session = question.session
        cv = session.cv

        job_description = ""

        missing_skills = []

        if session.job_analysis:
            job_description = (
                session.job_analysis.job_description
            )

            gap = calculate_skill_gap(
                cv.parsed_data.get(
                    "skills",
                    []
                ),
                session.job_analysis.required_skills,
            )

            missing_skills = gap[
                "missing_skills"
            ]

        evaluation = evaluate_answer(
            question=question.question_text,
            answer=answer_text,
            cv_text=cv.extracted_text,
            cv_data=cv.parsed_data,
            job_description=job_description,
            missing_skills=missing_skills,
        )

        score_match = re.search(
            r"SCORE:\s*(\d+(?:\.\d+)?)",
            evaluation,
            re.IGNORECASE,
        )

        score = (
            float(score_match.group(1))
            if score_match
            else 0
        )

        feedback_match = re.search(
            r"FEEDBACK:\s*(.*?)(?=\nSTRENGTHS:|$)",
            evaluation,
            re.IGNORECASE | re.DOTALL,
        )

        strengths_match = re.search(
            r"STRENGTHS:\s*(.*?)(?=\nIMPROVEMENTS:|$)",
            evaluation,
            re.IGNORECASE | re.DOTALL,
        )

        improvements_match = re.search(
            r"IMPROVEMENTS:\s*(.*?)(?=\nIMPROVED_ANSWER:|$)",
            evaluation,
            re.IGNORECASE | re.DOTALL,
        )

        improved_match = re.search(
            r"IMPROVED_ANSWER:\s*(.*)$",
            evaluation,
            re.IGNORECASE | re.DOTALL,
        )

        feedback = (
            feedback_match.group(1).strip()
            if feedback_match
            else evaluation
        )

        if strengths_match:
            feedback += (
                "\n\nStrengths:\n"
                + strengths_match.group(1).strip()
            )

        if improvements_match:
            feedback += (
                "\n\nImprovements:\n"
                + improvements_match.group(1).strip()
            )

        improved_answer = (
            improved_match.group(1).strip()
            if improved_match
            else ""
        )

        answer, _ = (
            InterviewAnswer.objects.update_or_create(
                question=question,
                defaults={
                    "answer_text": answer_text,
                    "score": score,
                    "feedback": feedback,
                    "improved_answer": improved_answer,
                },
            )
        )

        return Response({
            "question_id": question.id,
            "score": answer.score,
            "feedback": answer.feedback,
            "improved_answer": (
                answer.improved_answer
            ),
        })
        
class CompleteInterviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id):
        try:
            session = InterviewSession.objects.get(
                id=session_id,
                user=request.user,
            )
        except InterviewSession.DoesNotExist:
            return Response(
                {"detail": "Interview session not found."},
                status=404,
            )

        questions = session.questions.all()

        answered_questions = [
            question
            for question in questions
            if hasattr(question, "answer")
        ]

        scores = [
            question.answer.score
            for question in answered_questions
        ]

        final_score = (
            sum(scores) / len(scores)
            if scores
            else 0
        )

        session.final_score = round(
            final_score,
            2,
        )

        session.total_questions = questions.count()

        session.status = "completed"

        session.completed_at = timezone.now()

        session.save(
            update_fields=[
                "final_score",
                "total_questions",
                "status",
                "completed_at",
                "updated_at",
            ]
        )

        return Response({
            "session_id": session.id,
            "status": session.status,
            "final_score": session.final_score,
            "total_questions": session.total_questions,
            "completed_at": session.completed_at,
        })       
        
class InterviewHistoryView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sessions = (
            InterviewSession.objects
            .filter(
                user=request.user,
                status="completed",
            )
            .order_by("-completed_at")
        )

        data = [
            {
                "id": session.id,
                "role": session.role,
                "score": session.final_score,
                "total_questions": (
                    session.total_questions
                ),
                "completed_at": session.completed_at,
            }
            for session in sessions
        ]

        return Response(data)        
    
class InterviewHistoryView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sessions = (
            InterviewSession.objects
            .filter(
                user=request.user,
                status="completed",
            )
            .order_by("-completed_at")
        )

        data = []

        for session in sessions:
            answers = InterviewAnswer.objects.filter(
                question__session=session
            )

            scores = [
                answer.score
                for answer in answers
            ]

            data.append({
                "id": session.id,
                "role": session.role,
                "score": session.final_score,
                "total_questions": session.total_questions,
                "completed_at": session.completed_at,
                "answers_count": len(scores),
            })

        return Response(data)    