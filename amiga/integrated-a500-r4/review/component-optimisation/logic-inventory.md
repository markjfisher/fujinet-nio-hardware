# Complete 74-series inventory

2026-11-10; exported saved schematic. All MPNs below are Texas Instruments. Candidate IDs refer to review.md. Supplies are actual connected rails. Each single gate uses 1/1; each single DFF uses 1/1. Detailed pin nets and positions are in bom.csv.

| Ref | Exact MPN | Function / used | Rail; signal domain | Inputs → outputs / controls | Subsystem; disposition |
|---|---|---|---|---|---|
| U7 | SN74LVC1G04DBVR | inverter; 1/1 | 3V3_AON; 3.3 V internal | CC_LOW_CURRENT → POWER_ALLOW | power qualification; KEEP separate AON |
| U40 | SN74LVC541APWR | octal non-inverting tri-state; 8/8 | 3V3; host 5 V → 3.3 V | AMIGA_A1 → Z_A1; AMIGA_A2 → Z_A2; AMIGA_A3 → Z_A3; AMIGA_A4 → Z_A4; AMIGA_A5 → Z_A5; AMIGA_A6 → Z_A6; AMIGA_A7 → Z_A7; AMIGA_A8 → Z_A8; /OE pins 1=GND,19=GND | bus buffers; retain, wide-buffer option deferred |
| U41 | SN74LVC541APWR | octal non-inverting tri-state; 8/8 | 3V3; host 5 V → 3.3 V | AMIGA_A9 → Z_A9; AMIGA_A10 → Z_A10; AMIGA_A11 → Z_A11; AMIGA_A12 → Z_A12; AMIGA_A13 → Z_A13; AMIGA_A14 → Z_A14; AMIGA_A15 → Z_A15; AMIGA_A16 → Z_A16; /OE pins 1=GND,19=GND | bus buffers; retain, wide-buffer option deferred |
| U42 | SN74LVC541APWR | octal non-inverting tri-state; 8/8 | 3V3; host 5 V → 3.3 V | AMIGA_A17 → Z_A17; AMIGA_A18 → Z_A18; AMIGA_A19 → Z_A19; AMIGA_A20 → Z_A20; AMIGA_A21 → Z_A21; AMIGA_A22 → Z_A22; AMIGA_A23 → Z_A23; AMIGA_AS_N → Z_AS_N; /OE pins 1=GND,19=GND | bus buffers; retain, wide-buffer option deferred |
| U43 | SN74LVC541APWR | octal non-inverting tri-state; 5 host outputs + 1 constant / 8; six host inputs connected | 3V3; host 5 V → 3.3 V | UDS,LDS,READ,RESET,BERR → Z_UDS_N,Z_LDS_N,Z_READ,HOST_RESET_N,HOST_BERR_N; grounded channel drives Z_CFGIN_N; DTACK receiver output and eighth output NC; /OE pins 1=GND,19=GND | bus buffers; retain, wide-buffer option deferred |
| U44 | SN74LVC541APWR | octal non-inverting tri-state; 8/8 | 3V3; 3.3 V → host TTL (5 V bus) | Z_D0 → AMIGA_D0; Z_D1 → AMIGA_D1; Z_D2 → AMIGA_D2; Z_D3 → AMIGA_D3; Z_D4 → AMIGA_D4; Z_D5 → AMIGA_D5; Z_D6 → AMIGA_D6; Z_D7 → AMIGA_D7; /OE pins 1=TX_LO_N,19=GND | bus buffers; retain, wide-buffer option deferred |
| U45 | SN74LVC541APWR | octal non-inverting tri-state; 8/8 | 3V3; 3.3 V → host TTL (5 V bus) | Z_D8 → AMIGA_D8; Z_D9 → AMIGA_D9; Z_D10 → AMIGA_D10; Z_D11 → AMIGA_D11; Z_D12 → AMIGA_D12; Z_D13 → AMIGA_D13; Z_D14 → AMIGA_D14; Z_D15 → AMIGA_D15; /OE pins 1=TX_HI_N,19=GND | bus buffers; retain, wide-buffer option deferred |
| U46 | SN74LVC541APWR | octal non-inverting tri-state; 8/8 | 3V3; host 5 V → 3.3 V | AMIGA_D0 → Z_D0; AMIGA_D1 → Z_D1; AMIGA_D2 → Z_D2; AMIGA_D3 → Z_D3; AMIGA_D4 → Z_D4; AMIGA_D5 → Z_D5; AMIGA_D6 → Z_D6; AMIGA_D7 → Z_D7; /OE pins 1=RX_LO_N,19=GND | bus buffers; retain, wide-buffer option deferred |
| U47 | SN74LVC541APWR | octal non-inverting tri-state; 8/8 | 3V3; host 5 V → 3.3 V | AMIGA_D8 → Z_D8; AMIGA_D9 → Z_D9; AMIGA_D10 → Z_D10; AMIGA_D11 → Z_D11; AMIGA_D12 → Z_D12; AMIGA_D13 → Z_D13; AMIGA_D14 → Z_D14; AMIGA_D15 → Z_D15; /OE pins 1=RX_HI_N,19=GND | bus buffers; retain, wide-buffer option deferred |
| U61 | SN74LVC1G11DBVR | 3-input AND; 1/1 | 3V3; 3.3 V internal | HOST_PG, 3V3_PG, HOST_RESET_N → SAFE_POWER | hardware interlocks; I1 |
| U62 | SN74LVC1G11DBVR | 3-input AND; 1/1 | 3V3; 3.3 V internal | RP_RUN, RUN_MODE, BUS_ARM → SAFE_MODE | hardware interlocks; I1 |
| U63 | SN74LVC1G11DBVR | 3-input AND; 1/1 | 3V3; 3.3 V internal | SAFE_POWER, SAFE_MODE, BUS_READY → SAFE_BASE | hardware interlocks; I1 |
| U64 | SN74LVC1G04DBVR | inverter; 1/1 | 3V3; 3.3 V internal | Z_AS_N → AS_ACTIVE | hardware interlocks; I2 |
| U65 | SN74LVC1G04DBVR | inverter; 1/1 | 3V3; 3.3 V internal | Z_A20 → A20_LOW | hardware interlocks; I2 |
| U66 | SN74LVC1G11DBVR | 3-input AND; 1/1 | 3V3; 3.3 V internal | Z_A23, Z_A22, Z_A21 → IO_TOP | hardware interlocks; I1 |
| U67 | SN74LVC1G11DBVR | 3-input AND; 1/1 | 3V3; 3.3 V internal | IO_TOP, A20_LOW, Z_A19 → IO_WINDOW | hardware interlocks; I1 |
| U68 | SN74LVC1G11DBVR | 3-input AND; 1/1 | 3V3; 3.3 V internal | SAFE, AS_ACTIVE, IO_WINDOW → CYCLE_OK | hardware interlocks; I1 |
| U69 | SN74LVC1G04DBVR | inverter; 1/1 | 3V3; 3.3 V internal | Z_LDS_N → LO_ACTIVE | hardware interlocks; I2 |
| U70 | SN74LVC1G04DBVR | inverter; 1/1 | 3V3; 3.3 V internal | Z_UDS_N → HI_ACTIVE | hardware interlocks; I2 |
| U71 | SN74LVC1G11DBVR | 3-input AND; 1/1 | 3V3; 3.3 V internal | CYCLE_OK, Z_READ, DATA_VALID → READ_DRIVE | hardware interlocks; I1 |
| U72 | SN74LVC1G10DBVR | 3-input NAND; 1/1 | 3V3; 3.3 V internal | READ_DRIVE, LO_ACTIVE, 3V3 → TX_LO_N | hardware interlocks; I3 |
| U73 | SN74LVC1G10DBVR | 3-input NAND; 1/1 | 3V3; 3.3 V internal | READ_DRIVE, HI_ACTIVE, 3V3 → TX_HI_N | hardware interlocks; I3 |
| U74 | SN74LVC1G04DBVR | inverter; 1/1 | 3V3; 3.3 V internal | Z_READ → WRITE_CYCLE | hardware interlocks; I2 |
| U75 | SN74LVC1G04DBVR | inverter; 1/1 | 3V3; 3.3 V internal | DATA_VALID → DATA_RECEIVE | hardware interlocks; I2 |
| U76 | SN74LVC1G11DBVR | 3-input AND; 1/1 | 3V3; 3.3 V internal | CYCLE_OK, WRITE_CYCLE, DATA_RECEIVE → WRITE_RECEIVE | hardware interlocks; I1 |
| U77 | SN74LVC1G10DBVR | 3-input NAND; 1/1 | 3V3; 3.3 V internal | WRITE_RECEIVE, LO_ACTIVE, 3V3 → RX_LO_N | hardware interlocks; I3 |
| U78 | SN74LVC1G10DBVR | 3-input NAND; 1/1 | 3V3; 3.3 V internal | WRITE_RECEIVE, HI_ACTIVE, 3V3 → RX_HI_N | hardware interlocks; I3 |
| U79 | SN74LVC1G32DBVR | 2-input OR; 1/1 | 3V3; 3.3 V internal | LO_ACTIVE, HI_ACTIVE → ANY_LANE | hardware interlocks; KEEP single gate |
| U80 | SN74LVC1G11DBVR | 3-input AND; 1/1 | 3V3; 3.3 V internal | CYCLE_OK, WAIT_PENDING, 3V3 → WAIT_SINK | hardware interlocks; I1 |
| U81 | SN74LVC1G06DBVR | open-drain inverter; 1/1 | 3V3; 3.3 V internal; host open-drain output ≤5.5 V | WAIT_SINK → AMIGA_XRDY | hardware interlocks; I5 optional |
| U82 | SN74LVC1G08DBVR | 2-input AND; 1/1 | 3V3; 3.3 V internal | SAFE, IRQ_REQ → IRQ_SINK | hardware interlocks; I6 optional, prefer separate |
| U83 | SN74LVC1G06DBVR | open-drain inverter; 1/1 | 3V3; 3.3 V internal; host open-drain output ≤5.5 V | IRQ_SINK → AMIGA_INT2_N | hardware interlocks; I5 optional |
| U84 | SN74LVC1G74DCUR | positive-edge DFF, async /CLR,/PRE; 1/1 | 3V3; 3.3 V internal | CLK=ACK_REQ, D=ANY_LANE, /CLR=CYCLE_OK, /PRE=3V3; /Q=WAIT_PENDING, Q NC | cycle-state latches; I4 conditional |
| U85 | SN74LVC1G08DBVR | 2-input AND; 1/1 | 3V3; 3.3 V internal | SAFE_BASE, HOST_BERR_N → SAFE | hardware interlocks; I6 optional, prefer separate |
| U86 | SN74LVC1G74DCUR | positive-edge DFF, async /CLR,/PRE; 1/1 | 3V3; 3.3 V internal | CLK=DATA_DRIVE, D=3V3, /CLR=CYCLE_OK, /PRE=3V3; Q=DATA_VALID, /Q NC | cycle-state latches; I4 conditional |

All combinational control inputs are already in the 3.3 V domain; raw host signals enter through U40–U43. U81/U83 are the exceptions on the output side: they sink host-owned nets and must tolerate host voltage while off. U7 stays on AON. U40–U43 are always enabled; U44–U47 are qualified by independent byte/direction enables.

U43 has six host-connected receiver inputs, but its DTACK output is unconnected. Its grounded CFGIN channel supplies a constant low and its eighth input is tied low with output unconnected. This spare capacity does not eliminate an entire octal package.
