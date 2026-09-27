# Pinmap between 86 pin expansion and zorro-ii


| A500 pin | A500 signal                      | Zorro-II pinR/E | Zorro-II signal   | Mapping                            |
| -------- | -------------------------------- | --------------- | ----------------- | ---------------------------------- |
| 1        | GND                              | 1               | GND               | direct                             |
| 2        | GND                              | 2               | GND               | direct                             |
| 3        | GND                              | 3               | GND               | direct                             |
| 4        | GND                              | 4               | GND               | direct                             |
| 5        | +5V                              | 5               | +5V               | direct                             |
| 6        | +5V                              | 6               | +5V               | direct                             |
| **7**    | **NC**                           | —               | —                 | **no direct Zorro signal**         |
| **8**    | **−12V on A500 hardware/design** | **20**          | **−12V**          | **direct supply; also feeds 7905** |
| 9        | NC                               | —               | —                 | no direct mapping                  |
| 10       | +12V                             | 10              | +12V              | direct                             |
| 11       | NC                               | —               | —                 | no direct mapping                  |
| 12       | /CFGIN / grounded                | 12              | /CFGIN            | corresponding signal               |
| 13       | GND                              | 13              | GND               | direct                             |
| 14       | /C3                              | 14              | /C3               | direct                             |
| 15       | CDAC                             | 15              | CDAC              | direct                             |
| 16       | /C1                              | 16              | /C1               | direct                             |
| 17       | /OVR                             | 17              | /OVR              | direct                             |
| 18       | RDY                              | 18              | XRDY              | corresponding bus-ready signal     |
| 19       | /INT2                            | 19              | /INT2             | direct                             |
| **20**   | **NC on A500**                   | —               | —                 | no A500 signal                     |
| 21       | A5                               | 21              | A5                | direct                             |
| 22       | /INT6                            | 22              | /INT6             | direct                             |
| 23       | A6                               | 23              | A6                | direct                             |
| 24       | A4                               | 24              | A4                | direct                             |
| 25       | GND                              | 25              | GND               | direct                             |
| 26       | A3                               | 26              | A3                | direct                             |
| 27       | A2                               | 27              | A2                | direct                             |
| 28       | A7                               | 28              | A7                | direct                             |
| 29       | A1                               | 29              | A1                | direct logically                   |
| 30       | A8                               | 30              | A8                | direct                             |
| 31       | FC0                              | 31              | FC0               | direct                             |
| 32       | A9                               | 32              | A9                | direct                             |
| 33       | FC1                              | 33              | FC1               | direct                             |
| 34       | A10                              | 34              | A10               | direct                             |
| 35       | FC2                              | 35              | FC2               | direct                             |
| 36       | A11                              | 36              | A11               | direct                             |
| 37       | GND                              | 37              | GND               | direct                             |
| 38       | A12                              | 38              | A12               | direct                             |
| 39       | A13                              | 39              | A13               | direct                             |
| **40**   | **/IPL0**                        | —               | Zorro 40 = /EINT7 | **not the same signal**            |
| 41       | A14                              | 41              | A14               | direct                             |
| **42**   | **/IPL1**                        | —               | Zorro 42 = /EINT5 | **not the same signal**            |
| 43       | A15                              | 43              | A15               | direct                             |
| **44**   | **/IPL2**                        | —               | Zorro 44 = /EINT4 | **not the same signal**            |
| 45       | A16                              | 45              | A16               | direct                             |
| 46       | /BERR                            | 46              | /BERR             | direct                             |
| 47       | A17                              | 47              | A17               | direct                             |
| 48       | /VPA                             | 48              | /VPA              | corresponding signal               |
| 49       | GND                              | 49              | GND               | direct                             |
| 50       | E clock                          | 50              | E clock           | direct                             |
| 51       | /VMA                             | 51              | /VMA              | corresponding signal               |
| 52       | A18                              | 52              | A18               | direct                             |
| 53       | /RST                             | 53              | /RST              | direct                             |
| 54       | A19                              | 54              | A19               | direct                             |
| 55       | /HLT                             | 55              | /HLT              | direct                             |
| 56       | A20                              | 56              | A20               | direct                             |
| 57       | A22                              | 57              | A22               | direct                             |
| 58       | A21                              | 58              | A21               | direct                             |
| 59       | A23                              | 59              | A23               | direct                             |
| 60       | /BR                              | 60              | /BRn              | direct/corresponding               |
| 61       | GND                              | 61              | GND               | direct                             |
| 62       | /BGACK                           | 62              | /BGACK            | direct                             |
| 63       | D15                              | 63              | D15               | direct                             |
| 64       | /BG                              | 64              | /BGn              | direct/corresponding               |
| 65       | D14                              | 65              | D14               | direct                             |
| 66       | /DTACK                           | 66              | /DTACK            | direct                             |
| 67       | D13                              | 67              | D13               | direct                             |
| 68       | R/W                              | 68              | READ/RW           | direct                             |
| 69       | D12                              | 69              | D12               | direct                             |
| 70       | /LDS                             | 70              | /LDS              | direct                             |
| 71       | D11                              | 71              | D11               | direct                             |
| 72       | /UDS                             | 72              | /UDS              | direct                             |
| 73       | GND                              | 73              | GND               | direct                             |
| 74       | /AS                              | 74              | /AS               | direct                             |
| 75       | D0                               | 75              | D0                | direct                             |
| 76       | D10                              | 76              | D10               | direct                             |
| 77       | D1                               | 77              | D1                | direct                             |
| 78       | D9                               | 78              | D9                | direct                             |
| 79       | D2                               | 79              | D2                | direct                             |
| 80       | D8                               | 80              | D8                | direct                             |
| 81       | D3                               | 81              | D3                | direct                             |
| 82       | D7                               | 82              | D7                | direct                             |
| 83       | D4                               | 83              | D4                | direct                             |
| 84       | D6                               | 84              | D6                | direct                             |
| 85       | GND                              | 85              | GND               | direct                             |
| 86       | D5                               | 86              | D5                | direct                             |


