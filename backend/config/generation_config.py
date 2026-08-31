GENERATION_CONFIG = {

    # max_tokens is sized generously above the prompt's stated
    # word limit since Hindi/Marathi (Devanagari) tokenizes
    # less efficiently per word than English.

    "push": {
        "max_age_days": 3,
        "top_k": 1,
        "max_tokens": 200,
    },

    "whatsapp": {
        "max_age_days": 5,
        "top_k": 5,
        "max_tokens": 500,
    },

    "newsletter": {
        "max_age_days": 15,
        "top_k": 10,
        "max_tokens": 1200,
    },

}
