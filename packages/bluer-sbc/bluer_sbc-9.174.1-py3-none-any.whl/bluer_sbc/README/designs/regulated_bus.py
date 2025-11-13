from bluer_objects import README
from bluer_objects.README.items import ImageItems
from bluer_objects.README.consts import assets_url, designs_url

from bluer_sbc.README.design import design_doc


assets2 = assets_url(
    suffix="regulated-bus",
    volume=2,
)

marquee = README.Items(
    [
        {
            "name": "regulated bus",
            "marquee": f"{assets2}/20251112_214845.jpg",
            "url": "./bluer_sbc/docs/regulated-bus.md",
        }
    ]
)

items = ImageItems(
    {
        designs_url(
            "regulated-bus/wiring.png?raw=true",
        ): designs_url(
            "regulated-bus/wiring.svg",
        ),
        **{
            f"{assets2}/{timestamp}.jpg": ""
            for timestamp in [
                "20251112_214845",
            ]
        },
    }
)

parts = {
    "charging-port": "",
    "dsn-vc288": "",
    "XL4015": "",
    "white-terminal": "2 x",
    "pin-headers": "2 x (2 x 3, 90 degree)",
    "PCB-double-9x7": "10 x 15 holes",
}


docs = [
    design_doc(
        "regulated-bus",
        items,
        parts,
    )
]
