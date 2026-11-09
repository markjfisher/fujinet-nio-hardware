# A500 handshake correction and timing allocation

R2 circuit review, 2026-11-09. This supersedes R1's local-DTACK proposal.

## Why the circuit changed

The Commodore [A500/A2000 technical reference](https://erikarn.github.io/amiga/docs/Amiga_500_Technical_Reference.pdf),
printed page 91, says the motherboard normally generates /DTACK. Printed
page 94 specifies XRDY as the open-collector external wait input, asserted low
within 60ns of valid address (/AS assertion). Releasing XRDY allows the
motherboard acknowledgement to finish. These pages were read from the scan;
page 94 was also visually checked, avoiding the OCR's broken polarity text.
The A2000 PAL equations are not the basis for this A500 decision.

R1 drove /DTACK without suppressing the motherboard's acknowledgement.
That could finish a transfer before RP data was ready. It is not an acceptable
active-bus implementation. R2 removes that output entirely. /OVR remains NC.

## Implemented circuit

U81 now sinks **J40.18 XRDY**. J40.66 /DTACK connects only to a receiver input;
the native-netlist check explicitly rejects any additional connection there.
The address receiver and discrete gates assert WAIT_SINK when SAFE, /AS active,
the I/O region selected and the completion latch not set. The assertion path
does not wait for RP firmware or a synchronized GPIO sample.

U84 is SN74LVC1G74DCUR. Its asynchronous clear is CYCLE_OK, D is ANY_LANE,
clock is ACK_REQ, and inverted output is WAIT_PENDING. Outside a qualified
cycle it clears. A rising ACK_REQ with a valid byte strobe ends the wait;
holding ACK_REQ high across cycles cannot complete a subsequent cycle.

U86 is the same part: D=3V3, clock=DATA_DRIVE, clear=CYCLE_OK, Q=DATA_VALID.
Read output enable uses DATA_VALID. A request left high cannot drive the next
read until firmware returns it low and issues a fresh rising edge. Clearing
DATA_DRIVE alone does not disable this cycle's latched read driver; /AS ending
or loss of CYCLE_OK does. Firmware must not drop/change read data early.

The installed library has no 74LVC1G74 symbol. The pin-compatible
74AUC1G74 symbol is used with the explicit **SN74LVC1G74DCUR** fitted value.
Never substitute the AUC part. TI's DCU pin table matches the library:
1 CLK, 2 D, 3 /Q, 4 GND, 5 Q, 6 /CLR, 7 /PRE, 8 VCC. The searched footprint
is Package_SO:VSSOP-8_2.3x2mm_P0.5mm, identified as TI DCU0008A.

J40.46 /BERR now enters a spare U43 receiver channel and U85 qualifies SAFE.
A bus error therefore releases data outputs, XRDY and IRQ independently of
RP firmware. No extra GPIO is needed. No local pull-up is added to host nets.

## Preliminary timing budget

Use 3.3V +/-0.3V, manufacturer maximum propagation values through 125°C,
and the specified 50pF test conditions, rather than headline typical delays.

| Element | Maximum used | Manufacturer section |
| --- | ---: | --- |
| LVC541A input receiver | 5.6ns | [TI](https://www.ti.com/lit/ds/symlink/sn74lvc541a.pdf), switching characteristics through 125°C |
| LVC1G04 inverter | 4.2ns | [TI](https://www.ti.com/lit/ds/symlink/sn74lvc1g04.pdf), section 5.9 |
| LVC1G11 AND | 6.2ns | [TI](https://www.ti.com/lit/ds/symlink/sn74lvc1g11.pdf), section 5.8 |
| LVC1G06 sink | 4.5ns | [TI](https://www.ti.com/lit/ds/symlink/sn74lvc1g06.pdf), section 5.7 |

With SAFE established and U84 already cleared, the longest address path is
receiver + U66 + U67 + U68 + U80 + U81: **34.9ns**. The /AS path is receiver
+ U64 + U68 + U80 + U81: **26.7ns**. Allocate another 10ns for interconnect,
threshold differences and load uncertainty: the longest provisional allocation
is **44.9ns against 60ns**, leaving 15.1ns. This is a design budget, not measured
compliance. Check the actual host pull-up, fanout, input edge rate and extracted
load against the data-sheet conditions before calling this closed. If those
conditions do not hold, the budget must be recalculated or simulated.

The [flip-flop data sheet](https://www.ti.com/lit/ds/symlink/sn74lvc1g74.pdf),
sections 6.6–6.7, requires 2.7ns minimum clock/clear pulses and 1.2ns clear
recovery at 3.3V. Maximum clear-to-output is 7.9ns through 125°C; clock-to-/Q
is 8.2ns. A conservative interface requirement is at least 50ns /AS inactive
between cycles, allowing the receiver/clear path to settle. Verify this against
the supported stock A500 timing; accelerated hosts are not qualified here.
Do not use the static tests as evidence of metastability or glitch immunity.

## Firmware contract for this candidate

1. Keep BUS_READY low until the bus state machine is running, both request
   outputs are low and data GPIOs are inputs. Arm only while /AS is inactive.
2. Decode every cycle in E80000–EFFFFF. The coarse hardware window adds a wait
   even to addresses this board does not own. For those, release the wait with
   ACK_REQ and never claim read data. This first device has no passthrough;
   multi-board coexistence needs a separate review or narrower hardware decode.
3. For an owned read, preload the output value before making RP data pins
   outputs. Issue DATA_DRIVE only after CYCLE_OK has settled (initial firmware
   allocation: no earlier than 60ns after observed /AS assertion). Allow at
   least 100ns after that pulse before ACK_REQ. This deliberately exceeds the
   latch/gate/buffer delay budget; the active prototype must verify host setup.
4. For a write, leave RP data GPIOs as inputs and do not pulse DATA_DRIVE.
   Sample only asserted byte lanes, update local mailbox state, then pulse
   ACK_REQ. Acknowledge only with strobes valid. Request high and low times
   should each be at least 20ns; never hold a bus cycle waiting for USB/ESP.
5. Hold read value/direction until /AS releases; then return data GPIOs to
   inputs and both requests low before the next cycle. The external latches
   prevent stale TX claims but cannot change RP pad direction themselves.
6. Implement a bounded local service path and an independent RP watchdog that
   resets/disarms on a stalled handler. Hardware alone has no wait timeout:
   a hung RP can hold XRDY until /BERR, reset, disarming or power removal.
   This fault path remains an implementation/review obligation, not a proved
   automatic recovery claim. Existing USB recovery tests do not cover it.

PIO firmware is not changed in this hardware milestone. These obligations must
be implemented and verified before active attachment. Future measurements
should target XRDY assertion, read setup/hold, byte enables and release on the
new active board. The accepted passive captures and USB tests need no repeat.
