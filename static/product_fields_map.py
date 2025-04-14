from models import MaterialTypeEnum, MaterialThicknessEnum

product_fields_map = {
    "профиля": {
        "тип профиля": {"type": "input", "condition": "if not standard"},
        "длина профиля": {"type": "input"},
        "количество профиля": {"type": "input"},
        "материал": {
            "штрипс": {
                "оцинковка": [MaterialThicknessEnum.ZERO_FIVE, MaterialThicknessEnum.ONE, MaterialThicknessEnum.ONE_TWO],
            }
        },
    },
    "клямера": {
        "тип клямера": {"type": "select"},
        "количество": {"type": "input"},
        "материал": {
            "штрипс": {
                "нержавейка": [MaterialThicknessEnum.ONE, MaterialThicknessEnum.ONE_TWO],
                "оцинковка": [MaterialThicknessEnum.ONE, MaterialThicknessEnum.ONE_TWO],
            }
        },
    },
    "кронштейны": {
        "ширина": {"type": "input"},
        "длина": {"type": "input"},
        "количество": {"type": "input"},
        "материал": {
            "штрипс": {
                "оцинковка": [MaterialThicknessEnum.TWO],
            }
        },
    },
    "удлинители кронштейнов": {
        "ширина": {"type": "input"},
        "длина": {"type": "input"},
        "угловой?": {"type": "checkbox"},
        "количество": {"type": "input"},
        "материал": {
            "рулон": {
                "цинк": [MaterialThicknessEnum.ONE, MaterialThicknessEnum.ONE_TWO],
            },
            "листы": {
                "нержавейка": [MaterialThicknessEnum.ONE, MaterialThicknessEnum.ONE_TWO],
            }
        },
    },
    "кассеты": {
        "тип кассет": {"type": "select", "condition": "if other"},
        "количество": {"type": "input"},
        "материал": {
            "рулон": {
                "цинк": [MaterialThicknessEnum.ZERO_SEVEN, MaterialThicknessEnum.ONE, MaterialThicknessEnum.ONE_TWO],
                "полимер": [MaterialThicknessEnum.ZERO_SEVEN],
            },
            "листы": {
                "алюминий": [MaterialThicknessEnum.ONE, MaterialThicknessEnum.TWO],
                "оцинковка": [MaterialThicknessEnum.ONE_FIVE, MaterialThicknessEnum.TWO, MaterialThicknessEnum.THREE],
                "нержавейка": [MaterialThicknessEnum.ONE, MaterialThicknessEnum.ONE_TWO],
            },
        },
        "цвет": {"type": "input"},
        "красим?": {"type": "checkbox", "condition": "if not polymer"},
    },
    "линеарные панели": {
        "рабочая": {"type": "input"},
        "руст": {"type": "input"},
        "длина": {"type": "input"},
        "закрытые торцы?": {"type": "checkbox"},
        "количество": {"type": "input"},
        "материал": {
            "рулон": {
                "оцинковка": [MaterialThicknessEnum.ZERO_SEVEN],
                "полимер": [MaterialThicknessEnum.ZERO_SEVEN],
            },
        },
        "цвет": {"type": "input"},
        "красим?": {"type": "checkbox", "condition": "if not polymer"},
    },
    "фасонка": {
        "количество": {"type": "input"},
        "материал": {
            "рулон": {
                "полимер": [MaterialThicknessEnum.ZERO_FIVE, MaterialThicknessEnum.ZERO_SEVEN],
                "цинк": [MaterialThicknessEnum.ZERO_FIVE, MaterialThicknessEnum.ZERO_SEVEN, MaterialThicknessEnum.ONE, MaterialThicknessEnum.ONE_TWO],
            },
            "листы": {
                "цинк": [MaterialThicknessEnum.ONE_FIVE, MaterialThicknessEnum.TWO, MaterialThicknessEnum.THREE],
                "нержавейка": [MaterialThicknessEnum.ONE, MaterialThicknessEnum.ONE_TWO],
                "чернина": [MaterialThicknessEnum.ONE_FIVE, MaterialThicknessEnum.TWO],
                "алюминий": [MaterialThicknessEnum.ONE, MaterialThicknessEnum.TWO],
            },
        },
        "цвет": {"type": "input"},
        "красим?": {"type": "checkbox", "condition": "if not polymer"},
    },
    "листы": {
        "количество": {"type": "input"},
        "материал": {
            "рулон": {
                "полимер": [MaterialThicknessEnum.ZERO_FIVE, MaterialThicknessEnum.ZERO_SEVEN],
                "цинк": [MaterialThicknessEnum.ZERO_FIVE, MaterialThicknessEnum.ZERO_SEVEN, MaterialThicknessEnum.ONE, MaterialThicknessEnum.ONE_TWO],
            },
            "листы": {
                "цинк": [MaterialThicknessEnum.ONE_FIVE, MaterialThicknessEnum.TWO, MaterialThicknessEnum.THREE],
                "нержавейка": [MaterialThicknessEnum.ONE, MaterialThicknessEnum.ONE_TWO],
                "чернина": [MaterialThicknessEnum.ONE_FIVE, MaterialThicknessEnum.TWO],
                "алюминий": [MaterialThicknessEnum.ONE, MaterialThicknessEnum.TWO],
            },
        },
        "цвет": {"type": "input"},
        "красим?": {"type": "checkbox", "condition": "if not polymer"},
    },
    "стеновые панели": {
        "количество": {"type": "input"},
        "материал": {
            "листы": {
                "чернина": [MaterialThicknessEnum.ONE_FIVE, MaterialThicknessEnum.TWO],
                "цинк": [MaterialThicknessEnum.ONE_TWO, MaterialThicknessEnum.ONE_FIVE, MaterialThicknessEnum.TWO],
            }
        },
    },
    "другое": {
        "количество": {"type": "input"},
        "материал": {
            "штрипс": {
                "цинк": [MaterialThicknessEnum.ZERO_FIVE, MaterialThicknessEnum.ONE, MaterialThicknessEnum.ONE_TWO, MaterialThicknessEnum.TWO],
                "нержавейка": [MaterialThicknessEnum.ONE, MaterialThicknessEnum.ONE_TWO],
            },
            "рулон": {
                "цинк": [MaterialThicknessEnum.ZERO_FIVE, MaterialThicknessEnum.ZERO_SEVEN, MaterialThicknessEnum.ONE, MaterialThicknessEnum.ONE_TWO],
                "полимер": [MaterialThicknessEnum.ZERO_FIVE, MaterialThicknessEnum.ZERO_SEVEN],
            },
            "листы": {
                "алюминий": [MaterialThicknessEnum.ONE, MaterialThicknessEnum.TWO],
                "нержавейка": [MaterialThicknessEnum.ONE, MaterialThicknessEnum.ONE_TWO],
                "цинк": [MaterialThicknessEnum.ONE_FIVE, MaterialThicknessEnum.TWO, MaterialThicknessEnum.THREE],
                "чернина": [MaterialThicknessEnum.ONE_FIVE, MaterialThicknessEnum.TWO],
            }
        },
        "цвет": {"type": "input"},
        "красим?": {"type": "checkbox", "condition": "if not polymer"},
    },
}
