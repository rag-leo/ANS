class MetadataService:

    KEYWORD_CROPS = [
        "कापूस",
        "सोयाबीन",
        "ऊस",
        "तूर",
        "हरभरा",
        "गहू",
        "केळी",
        "द्राक्ष",
        "कांदा",
        "मका",
        "टोमॅटो",
        "मिरची",
        "डाळिंब",
        "केळी", 
        "मिरची", 
        "भुईमूग", 
        "मका", 
        "कांदा", 
        "भात", 
        "डाळिंब", 
        "बटाटा",
    ]

    CATEGORY_RULES = {

        "Weather": [
            "पाऊस",
            "हवामान",
            "rain",
            "weather",
            "मान्सून",
        ],

        "Market Intelligence": [
            "दर",
            "भाव",
            "बाजार",
            "market",
            "price",
            "आवक",
            "निर्यात",
        ],

        "Policy": [
            "योजना",
            "सरकार",
            "अनुदान",
            "कर्जमाफी",
            "विमा",
        ],

        "Technology": [
            "तंत्रज्ञान",
            "drip",
            "irrigation",
            "mechanization",
        ],

        "Politics": [
            "मोर्चा",
            "आंदोलन",
            "खासदार",
            "संसद",
            "पक्ष",
            "निवडणूक",
        ],

        "Administration": [
            "नियुक्त",
            "बैठक",
            "अधिकारी",
            "महामंडळ",
            "विभाग",
        ],

        "Livestock": [
            "दूध",
            "पशुधन",
            "दुग्ध",
            "गोपाळ",
        ],

        "Research": [
            "अहवाल",
            "report",
            "survey",
            "study",
        ],

        "Crop Advisory": [

            "फवारणी",
            "कीड",
            "रोग",
            "नियोजन",
            "व्यवस्थापन",
            "खत",
            "पाणी व्यवस्थापन",
            "crop management",
            "spraying",

        ]        
    }

    NON_CROP_CATEGORIES = [] # add categories for which you want suppress crop assignment

    TITLE_WEIGHT = 5

    CONTENT_WEIGHT = 1

    MIN_CROP_SCORE = 3

    CATEGORY_TITLE_WEIGHT = 10

    CATEGORY_CONTENT_WEIGHT = 1

    MIN_CATEGORY_SCORE = 3


    @classmethod
    def extract_metadata(
        cls,
        title: str,
        content: str,
    ) -> dict:

        title = title or ""

        content = content or ""

        category_scores = {}

        title_lower = title.lower()

        content_lower = content.lower()

        for category_name, keywords in (
            cls.CATEGORY_RULES.items()
        ):

            score = 0

            for keyword in keywords:

                keyword = keyword.lower()

                if keyword in title_lower:

                    score += (
                        cls.CATEGORY_TITLE_WEIGHT
                    )

                score += (
                    content_lower.count(
                        keyword
                    )
                    * cls.CATEGORY_CONTENT_WEIGHT
                )

            category_scores[
                category_name
            ] = score

        best_category = max(
            category_scores,
            key=category_scores.get,
        )

        if (
            category_scores[
                best_category
            ] >= cls.MIN_CATEGORY_SCORE
        ):
            category = best_category

            print("\n-------------------")

            print(
                f"TITLE: {title}"
            )

            print(
                f"CATEGORY SCORES: "
                f"{category_scores}"
            )

            print(
                f"SELECTED CATEGORY: "
                f"{category}"
            )

            print("-------------------")

        else:
            category = "General"

        # -------------------------
        # Crop Extraction
        # -------------------------

        crop_scores = {}

        if category not in (
            cls.NON_CROP_CATEGORIES
        ):

            for crop in cls.KEYWORD_CROPS:

                score = 0

                if crop in title:
                    score += (
                        cls.TITLE_WEIGHT
                    )

                content_count = (
                    content.count(crop)
                )

                score += (
                    content_count
                    * cls.CONTENT_WEIGHT
                )

                crop_scores[crop] = (
                    score
                )

            crops = [
                crop
                for crop, score in (
                    crop_scores.items()
                )
                if score >= (
                    cls.MIN_CROP_SCORE
                )
            ]

        else:

            crops = []

        return {
            "crop": crops,
            "category": category,
            "keywords": crops,
            "confidence": crop_scores,
        }