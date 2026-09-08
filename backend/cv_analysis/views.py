from __future__ import annotations

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from cvs.models import CV
from cv_analysis.models import CVAnalysis

from cv_analysis.services.cv_scorer import (
    calculate_cv_score,
)

from cv_analysis.services.ats_analyzer import (
    analyze_ats,
)

from career_taxonomy.services.career_intelligence import (
    analyze_candidate_career,
)


class CVAnalysisView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    # ========================================================
    # GET - Retrieve Existing CV Analysis
    # ========================================================

    def get(self, request, cv_id):

        # ----------------------------------------------------
        # 1. Get CV
        # ----------------------------------------------------

        try:
            cv = CV.objects.get(
                id=cv_id,
                user=request.user,
            )

        except CV.DoesNotExist:

            return Response(
                {
                    "status": "error",
                    "message": "CV not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # ----------------------------------------------------
        # 2. Get Existing Analysis
        # ----------------------------------------------------

        try:
            analysis = CVAnalysis.objects.get(
                cv=cv
            )

        except CVAnalysis.DoesNotExist:

            return Response(
                {
                    "status": "not_analyzed",
                    "message": "This CV has not been analyzed yet.",
                    "cv_id": cv.id,
                    "cv_title": getattr(
                        cv,
                        "title",
                        None,
                    ),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # ----------------------------------------------------
        # 3. Extract stored data
        # ----------------------------------------------------

        breakdown = (
            analysis.breakdown
            or {}
        )

        sections = (
            analysis.sections
            or {}
        )

        ats_result = breakdown.get(
            "ats",
            {},
        )

        career_intelligence = (
            breakdown.get(
                "career_intelligence",
                {},
            )
        )

        # ----------------------------------------------------
        # 4. Return Existing Analysis
        # ----------------------------------------------------

        return Response(
            {
                "status": "success",

                "cv_id": cv.id,

                "cv_title": getattr(
                    cv,
                    "title",
                    None,
                ),

                "score": analysis.score,

                "breakdown": breakdown,

                "sections": sections,

                # --------------------------------------------
                # ATS
                # --------------------------------------------

                "ats": ats_result,

                "ats_score": ats_result.get(
                    "score",
                    0,
                ),

                "ats_status": ats_result.get(
                    "status",
                    "unknown",
                ),

                # --------------------------------------------
                # Career Intelligence
                # --------------------------------------------

                "career_intelligence": (
                    career_intelligence
                ),
            },

            status=status.HTTP_200_OK,
        )

    # ========================================================
    # POST - Analyze CV
    # ========================================================

    def post(self, request, cv_id):

        # ====================================================
        # 1. Get CV
        # ====================================================

        try:
            cv = CV.objects.get(
                id=cv_id,
                user=request.user,
            )

        except CV.DoesNotExist:

            return Response(
                {
                    "status": "error",
                    "message": "CV not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # ====================================================
        # 2. Get Parsed CV Data
        # ====================================================

        parsed_data = (
            cv.parsed_data
            or {}
        )

        extracted_text = (
            cv.extracted_text
            or ""
        )

        # ====================================================
        # 3. Existing CV Score
        # ====================================================

        try:

            cv_result = calculate_cv_score(
                parsed_data=parsed_data,
                extracted_text=extracted_text,
            )

        except TypeError:

            cv_result = calculate_cv_score(
                parsed_data,
                extracted_text,
            )

        # ====================================================
        # 4. Normalize CV Score Result
        # ====================================================

        if isinstance(
            cv_result,
            dict,
        ):

            score = cv_result.get(
                "score",
                0,
            )

            breakdown = cv_result.get(
                "breakdown",
                {},
            )

            sections = cv_result.get(
                "sections",
                {},
            )

        else:

            score = float(
                cv_result or 0
            )

            breakdown = {}
            sections = {}

        # Make sure score is valid.
        try:
            score = max(
                0,
                min(
                    float(score),
                    100,
                ),
            )
        except (
            TypeError,
            ValueError,
        ):
            score = 0

        # ====================================================
        # 5. ATS Analysis
        # ====================================================

        try:

            ats_result = analyze_ats(
                parsed_data=parsed_data,
                extracted_text=extracted_text,
            )

        except TypeError:

            ats_result = analyze_ats(
                parsed_data,
                extracted_text,
            )

        if not isinstance(
            ats_result,
            dict,
        ):

            ats_result = {
                "score": 0,
                "status": "unknown",
            }

        ats_score = ats_result.get(
            "score",
            0,
        )

        ats_status = ats_result.get(
            "status",
            "unknown",
        )

        # ====================================================
        # 6. Career Intelligence
        # ====================================================

        try:

            career_intelligence = (
                analyze_candidate_career(
                    parsed_data=parsed_data,
                    extracted_text=extracted_text,
                    cv_score=score,
                    top_n=5,
                )
            )

        except Exception as exc:

            # Career Intelligence should NEVER
            # break the normal CV analysis.

            career_intelligence = {
                "status": "error",

                "message": (
                    "Career Intelligence could not be calculated."
                ),

                "error": str(exc),

                "candidate_profile": None,

                "career_detection": {
                    "status": "error",
                    "best_role": None,
                    "top_roles": [],
                    "count": 0,
                },

                "primary_role": None,

                "skill_gap": None,

                "roadmap": None,

                "career_readiness": None,
            }

        # ====================================================
        # 7. Normalize Breakdown
        # ====================================================

        if not isinstance(
            breakdown,
            dict,
        ):
            breakdown = {}

        # Save ATS inside breakdown.
        breakdown["ats"] = ats_result

        # Save COMPLETE Career Intelligence.
        #
        # Important:
        # Don't only save primary_role here.
        # We want the frontend to have access to:
        #
        # - candidate_profile
        # - top roles
        # - skill gap
        # - roadmap
        # - readiness
        #
        breakdown["career_intelligence"] = (
            career_intelligence
        )

        # ====================================================
        # 8. Save / Update CV Analysis
        # ====================================================

        analysis, created = (
            CVAnalysis.objects.update_or_create(
                cv=cv,

                defaults={
                    # PositiveIntegerField
                    "score": int(
                        round(score)
                    ),

                    "breakdown": breakdown,

                    "sections": sections,
                },
            )
        )

        # ====================================================
        # 9. Response
        # ====================================================

        return Response(
            {
                "status": "success",

                "cv_id": cv.id,

                "cv_title": getattr(
                    cv,
                    "title",
                    None,
                ),

                "score": score,

                "breakdown": breakdown,

                "sections": sections,

                # --------------------------------------------
                # ATS
                # --------------------------------------------

                "ats": ats_result,

                "ats_score": ats_score,

                "ats_status": ats_status,

                # --------------------------------------------
                # Career Intelligence
                # --------------------------------------------

                "career_intelligence": (
                    career_intelligence
                ),
            },

            status=status.HTTP_200_OK,
        )