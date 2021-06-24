"""
This UPDI interface is not documented in the atdef. Hand defined here from ATtiny814 datasheet
"""
UPDI_INTERFACE = {
    "id": "UPDI",
    "caption": "Unified Program and Debug Interface",
    "name": "UPDI",
    "register_groups": [
        {
            "caption": "Unified Program and Debug Interface",
            "name": "UPDI",
            "size": "0x0D",
            "registers": [
                {
                    "caption": "Status A",
                    "reset": "0x20",
                    "name": "STATUSA",
                    "offset": "0x0",
                    "rw": "R",
                    "size": 1,
                    "bitfields": [
                        {
                            "caption": "UPDI Revision",
                            "mask": "0xf0",
                            "name": "UPDIREV",
                            "rw": "R",
                        }
                    ]
                },
                {
                    "caption": "Status B",
                    "reset": "0x00",
                    "name": "STATUSB",
                    "offset": "0x1",
                    "rw": "R",
                    "size": 1,
                    "bitfields": [
                        {
                            "caption": "UPDI Error Signature",
                            "mask": "0x7",
                            "name": "PESIG",
                            "rw": "R",
                        }
                    ]
                },
                {
                    "caption": "Control A",
                    "reset": "0x00",
                    "name": "CTRLA",
                    "offset": "0x2",
                    "rw": "RW",
                    "size": 1,
                    "bitfields": [
                        {
                            "caption": "Inter-Byte Delay Enable",
                            "mask": "0x80",
                            "name": "IBDLY",
                            "rw": "RW",
                        },
                        {
                            "caption": "Parity Disable",
                            "mask": "0x20",
                            "name": "PARD",
                            "rw": "RW",
                        },
                        {
                            "caption": "Disable Time-Out Detection",
                            "mask": "0x10",
                            "name": "DTD",
                            "rw": "RW",
                        },
                        {
                            "caption": "Response Signature Disable",
                            "mask": "0x8",
                            "name": "RSD",
                            "rw": "RW",
                        },
                        {
                            "caption": "Guard Time Value",
                            "mask": "0x7",
                            "name": "GTVAL",
                            "rw": "RW",
                        },
                    ]
                },
                {
                    "caption": "Control B",
                    "reset": "0x00",
                    "name": "CTRLB",
                    "offset": "0x3",
                    "rw": "RW",
                    "size": 1,
                    "bitfields": [
                        {
                            "caption": "Disable Nack Response",
                            "mask": "0x10",
                            "name": "NACKDIS",
                            "rw": "RW",
                        },
                        {
                            "caption": "Collision and Contention Detection Disable",
                            "mask": "0x8",
                            "name": "CCDETDIS",
                            "rw": "RW",
                        },
                        {
                            "caption": "UPDI Disalbe",
                            "mask": "0x4",
                            "name": "UPDIDIS",
                            "rw": "RW",
                        }
                    ]
                },
                {
                    "caption": "Control B",
                    "reset": "0x00",
                    "name": "CTRLB",
                    "offset": "0x3",
                    "rw": "RW",
                    "size": 1,
                    "bitfields": [
                        {
                            "caption": "Disable Nack Response",
                            "mask": "0x10",
                            "name": "NACKDIS",
                            "rw": "RW",
                        },
                        {
                            "caption": "Collision and Contention Detection Disable",
                            "mask": "0x8",
                            "name": "CCDETDIS",
                            "rw": "RW",
                        },
                        {
                            "caption": "UPDI Disable",
                            "mask": "0x4",
                            "name": "UPDIDIS",
                            "rw": "RW",
                        }
                    ]
                },
                {
                    "caption": "ASI Key Status",
                    "reset": "0x00",
                    "name": "ASI_KEY_STATUS",
                    "offset": "0x7",
                    "rw": "RW",
                    "size": 1,
                    "bitfields": [
                        {
                            "caption": "User Row Write Key Status",
                            "mask": "0x20",
                            "name": "UROWWRITE",
                            "rw": "RW",
                        },
                        {
                            "caption": "NVM Programming Key Status",
                            "mask": "0x10",
                            "name": "NVMPROG",
                            "rw": "R",
                        },
                        {
                            "caption": "Chip Erase Key Status",
                            "mask": "0x8",
                            "name": "CHIPERASE",
                            "rw": "R",
                        }
                    ]
                },
                {
                    "caption": "ASI Reset Request",
                    "reset": "0x00",
                    "name": "ASI_RESET_REQ",
                    "offset": "0x8",
                    "rw": "RW",
                    "size": 1,
                    "bitfields": [
                        {
                            "caption": "Reset Request",
                            "mask": "0xff",
                            "name": "RSTREQ",
                            "rw": "RW",
                        }
                    ]
                },
                {
                    "caption": "ASI Control A",
                    "reset": "0x03",
                    "name": "ASI_CTRLA",
                    "offset": "0x9",
                    "rw": "RW",
                    "size": 1,
                    "bitfields": [
                        {
                            "caption": "UPDI Clock Divider Select",
                            "mask": "0x3",
                            "name": "UPDICLKSEL",
                            "rw": "RW",
                        }
                    ]
                },
                {
                    "caption": "ASI System Control A",
                    "reset": "0x00",
                    "name": "ASI_SYS_CTRLA",
                    "offset": "0xA",
                    "rw": "RW",
                    "size": 1,
                    "bitfields": [
                        {
                            "caption": "User Row Programming Done",
                            "mask": "0x2",
                            "name": "UROWWRITE_FINAL",
                            "rw": "RW",
                        },
                        {
                            "caption": "Request System Clock",
                            "mask": "0x1",
                            "name": "CLKREQ",
                            "rw": "RW",
                        },
                    ]
                },
                {
                    "caption": " ASI System Status",
                    "reset": "0x01",
                    "name": "ASI_SYS_STATUS",
                    "offset": "0xb",
                    "rw": "R",
                    "size": 1,
                    "bitfields": [
                        {
                            "caption": "System Reset Active",
                            "mask": "0x20",
                            "name": "RSTSYS",
                            "rw": "R",
                        },
                        {
                            "caption": "System Domain in Sleep",
                            "mask": "0x10",
                            "name": "INSLEEP",
                            "rw": "R",
                        },
                        {
                            "caption": "Start NVM Programming",
                            "mask": "0x8",
                            "name": "NVMPROG",
                            "rw": "R",
                        },
                        {
                            "caption": "Start User Row Programming",
                            "mask": "0x4",
                            "name": "UROWPROG",
                            "rw": "R",
                        },
                        {
                            "caption": "NVM Lock Status",
                            "mask": "0x1",
                            "name": "LOCKSTATUS",
                            "rw": "R",
                        }
                    ]
                },
                {
                    "caption": "ASI CRC Status",
                    "reset": "0x00",
                    "name": "ASI_CRC_STATUS",
                    "offset": "0xc",
                    "rw": "R",
                    "size": 1,
                    "bitfields": [
                        {
                            "caption": "CRC Execution Status",
                            "mask": "0x7",
                            "name": "CRC_STATUS",
                            "rw": "R",
                        },
                    ]
                },
            ]
        }
    ],
}
