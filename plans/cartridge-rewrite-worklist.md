# Cartridge → terra conversion worklist (driven by dry-run; do in KiCad GUI)

Server: http://127.0.0.1:8361 (terra HTTP lib, wired globally). Swap each part to the listed terra unique_id; KiCad embeds the symbol + maps pins by number; verify placement; then `kicad-cli sch export netlist` before/after must match.

## CONVERT (87) — ref → terra part

### Capacitor (17)
- `C10` [A] → **Murata-GRM155Z71A105KE01D**  (mpn `GRM155Z71A105KE01D`, value `1u`, fp `Capacitor_SMD:C_0402_1005Metric`)
- `C11` [B] → **Samsung-CL05B104KO5NNN**  (mpn `CL05B104KO5NNN`, value `100n`, fp `Capacitor_SMD:C_0402_1005Metric`)
- `C12` [A] → **Murata-GRM155Z71A105KE01D**  (mpn `GRM155Z71A105KE01D`, value `1u`, fp `Capacitor_SMD:C_0402_1005Metric`)
- `C13` [B] → **Samsung-CL05B104KO5NNN**  (mpn `CL05B104KO5NNN`, value `100n`, fp `Capacitor_SMD:C_0402_1005Metric`)
- `C14` [A] → **Murata-GRM155Z71A105KE01D**  (mpn `GRM155Z71A105KE01D`, value `1u`, fp `Capacitor_SMD:C_0402_1005Metric`)
- `C15` [B] → **Samsung-CL05B104KO5NNN**  (mpn `CL05B104KO5NNN`, value `100n`, fp `Capacitor_SMD:C_0402_1005Metric`)
- `C16` [B] → **Samsung-CL05B104KO5NNN**  (mpn `CL05B104KO5NNN`, value `100n`, fp `Capacitor_SMD:C_0402_1005Metric`)
- `C17` [A] → **Murata-GRM155Z71A105KE01D**  (mpn `GRM155Z71A105KE01D`, value `1u`, fp `Capacitor_SMD:C_0402_1005Metric`)
- `C18` [B] → **Samsung-CL05A106MP68UN**  (mpn `CL05A106MP68UN`, value `10u`, fp `Capacitor_SMD:C_0402_1005Metric`)
- `C2` [A] → **Murata-GRM155Z71A105KE01D**  (mpn `GRM155Z71A105KE01D`, value `1u`, fp `Capacitor_SMD:C_0402_1005Metric`)
- `C3` [B] → **Samsung-CL05B104KO5NNN**  (mpn `CL05B104KO5NNN`, value `100n`, fp `Capacitor_SMD:C_0402_1005Metric`)
- `C4` [B] → **Samsung-CL05A106MP68UN**  (mpn `CL05A106MP68UN`, value `10u`, fp `Capacitor_SMD:C_0402_1005Metric`)
- `C5` [B] → **Samsung-CL05B104KO5NNN**  (mpn `CL05B104KO5NNN`, value `100n`, fp `Capacitor_SMD:C_0402_1005Metric`)
- `C6` [B] → **Samsung-CL05A106MP68UN**  (mpn `CL05A106MP68UN`, value `10u`, fp `Capacitor_SMD:C_0402_1005Metric`)
- `C7` [B] → **Samsung-CL05B104KO5NNN**  (mpn `CL05B104KO5NNN`, value `100n`, fp `Capacitor_SMD:C_0402_1005Metric`)
- `C8` [A] → **Murata-GRM155Z71A105KE01D**  (mpn `GRM155Z71A105KE01D`, value `1u`, fp `Capacitor_SMD:C_0402_1005Metric`)
- `C9` [B] → **Samsung-CL05B104KO5NNN**  (mpn `CL05B104KO5NNN`, value `100n`, fp `Capacitor_SMD:C_0402_1005Metric`)

### Connector (3)
- `J1` [A] → **Mill-Max-829-22-008-20-002101**  (mpn `829-22-008-20-002101`, value `8 pins`, fp `terra-connectors:MillMax_829-22-004-20-002101_pogo_RA_8pin`)
- `J2` [A] → **Molex-5600200320**  (mpn `5600200320`, value `Solenoid`, fp `terra-connectors:Molex_5600200320_3pin_DuraClick_SMT`)
- `J3` [A] → **Molex-532540470**  (mpn `532540470`, value `connector`, fp `terra-connectors:Molex_Micro-Latch_53254-0470_1x04_P2.00mm_Horizontal`)

### Diode/TVS (6)
- `D1` [A] → **Vishay-VSSAF512**  (mpn `VSSAF512`, value `VSSAF512`, fp `terra_sym:Vishay_SlimSMA_D_DO-221AC`)
- `D2` [A] → **Diodes, Inc.-MMBD914-7-F**  (mpn `MMBD914-7-F`, value `MMBD914`, fp `Package_TO_SOT_SMD:SOT-23`)
- `D3` [A] → **Diodes, Inc.-MMBD914-7-F**  (mpn `MMBD914-7-F`, value `MMBD914`, fp `Package_TO_SOT_SMD:SOT-23`)
- `D4` [A] → **Diodes, Inc.-MMBD914-7-F**  (mpn `MMBD914-7-F`, value `MMBD914`, fp `Package_TO_SOT_SMD:SOT-23`)
- `D6` [A] → **Nexperia-PNE20020ER**  (mpn `PNE20020ER`, value `200V 2.8A`, fp `terra_sym:Nexperia SOD-123W`)
- `D8` [A] → **Nexperia-PNE20020ER**  (mpn `PNE20020ER`, value `200V 2.8A`, fp `terra_sym:Nexperia SOD-123W`)

### Ferrite (7)
- `FB1` [A] → **Murata-BLM18BD221SN1D**  (mpn `BLM18BD221SN1D`, value `220Ω 250mA`, fp `Inductor_SMD:L_0603_1608Metric`)
- `FB2` [A] → **Murata-BLM18BD221SN1D**  (mpn `BLM18BD221SN1D`, value `220Ω 250mA`, fp `Inductor_SMD:L_0603_1608Metric`)
- `FB3` [A] → **Murata-BLM18BD221SN1D**  (mpn `BLM18BD221SN1D`, value `220Ω 250mA`, fp `Inductor_SMD:L_0603_1608Metric`)
- `FB4` [A] → **Murata-BLM18BD221SN1D**  (mpn `BLM18BD221SN1D`, value `220Ω 250mA`, fp `Inductor_SMD:L_0603_1608Metric`)
- `FB5` [A] → **Murata-BLM18BD221SN1D**  (mpn `BLM18BD221SN1D`, value `220Ω 250mA`, fp `Inductor_SMD:L_0603_1608Metric`)
- `FB6` [A] → **Murata-BLM18BD221SN1D**  (mpn `BLM18BD221SN1D`, value `220Ω 250mA`, fp `Inductor_SMD:L_0603_1608Metric`)
- `FB7` [A] → **Murata-BLM18BD221SN1D**  (mpn `BLM18BD221SN1D`, value `220Ω 250mA`, fp `Inductor_SMD:L_0603_1608Metric`)

### IC (4)
- `U1` [A] → **Microchip-ATSAMC20G18A**  (mpn `ATSAMC20G18A`, value `ATSAMC20G18A`, fp `Package_QFP:TQFP-48_7x7mm_P0.5mm`)
- `U2` [A] → **Analog Devices-MAX3488EESA+**  (mpn `MAX3488EESA+`, value `RS422`, fp `Package_SO:SOIC-8_3.9x4.9mm_P1.27mm`)
- `U4` [A] → **Texas Instruments-TL081HIDBVR**  (mpn `TL081HIDBVR`, value `TL081H`, fp `Package_TO_SOT_SMD:SOT-23-5`)
- `U5` [A] → **Microchip- 24LC32AT-I/OT**  (mpn ` 24LC32AT-I/OT`, value `4k x 8 EEPROM`, fp `terra_sym:SOT95P270X145-5N`)

### Resistor (26)
- `R1` [A] → **Panasonic-ERJ1TRQF6R8U**  (mpn `ERJ1TRQF6R8U`, value `6.8`, fp `Resistor_SMD:R_2512_6332Metric`)
- `R10` [B] → **Yageo-RT0603FKE07100RL**  (mpn `RT0603FKE07100RL`, value `100`, fp `Resistor_SMD:R_0603_1608Metric`)
- `R11` [B] → **Yageo-RT0603FKE071KL**  (mpn `RT0603FKE071KL`, value `1K`, fp `Resistor_SMD:R_0603_1608Metric`)
- `R12` [B] → **Yageo-RT0603FKE0751K1L**  (mpn `RT0603FKE0751K1L`, value `51.1K`, fp `Resistor_SMD:R_0603_1608Metric`)
- `R13` [B] → **Yageo-RT0603FKE0715KL**  (mpn `RT0603FKE0715KL`, value `15K`, fp `Resistor_SMD:R_0603_1608Metric`)
- `R15` [B] → **Yageo-RT0603FKE07100RL**  (mpn `RT0603FKE07100RL`, value `100`, fp `Resistor_SMD:R_0603_1608Metric`)
- `R16` [B] → **Yageo-RT0603FKE0710KL**  (mpn `RT0603FKE0710KL`, value `10K`, fp `Resistor_SMD:R_0603_1608Metric`)
- `R17` [B] → **Yageo-RT0603FKE074K7L**  (mpn `RT0603FKE074K7L`, value `4.7K`, fp `Resistor_SMD:R_0603_1608Metric`)
- `R18` [B] → **Yageo-RT0603FKE074K7L**  (mpn `RT0603FKE074K7L`, value `4.7K`, fp `Resistor_SMD:R_0603_1608Metric`)
- `R19` [B] → **Yageo-RT0603FKE074K7L**  (mpn `RT0603FKE074K7L`, value `4.7K`, fp `Resistor_SMD:R_0603_1608Metric`)
- `R2` [B] → **Yageo-RT0603FKE071KL**  (mpn `RT0603FKE071KL`, value `1K`, fp `Resistor_SMD:R_0603_1608Metric`)
- `R20` [B] → **Yageo-RT0603FKE074K7L**  (mpn `RT0603FKE074K7L`, value `4.7K`, fp `Resistor_SMD:R_0603_1608Metric`)
- `R22` [B] → **Yageo-RT0603FKE07120RL**  (mpn `RT0603FKE07120RL`, value `120`, fp `Resistor_SMD:R_0603_1608Metric`)
- `R23` [B] → **Yageo-RT0603FKE0747RL**  (mpn `RT0603FKE0747RL`, value `47`, fp `Resistor_SMD:R_0603_1608Metric`)
- `R24` [B] → **Yageo-RT0603FKE0747RL**  (mpn `RT0603FKE0747RL`, value `47`, fp `Resistor_SMD:R_0603_1608Metric`)
- `R25` [B] → **Yageo-RT0603FKE0751K1L**  (mpn `RT0603FKE0751K1L`, value `51.1K`, fp `Resistor_SMD:R_0603_1608Metric`)
- `R26` [B] → **Yageo-RT0603FKE0751K1L**  (mpn `RT0603FKE0751K1L`, value `51.1K`, fp `Resistor_SMD:R_0603_1608Metric`)
- `R27` [B] → **Yageo-RT0603FKE0751K1L**  (mpn `RT0603FKE0751K1L`, value `51.1K`, fp `Resistor_SMD:R_0603_1608Metric`)
- `R28` [B] → **Yageo-RT0603FKE0751K1L**  (mpn `RT0603FKE0751K1L`, value `51.1K`, fp `Resistor_SMD:R_0603_1608Metric`)
- `R3` [B] → **Yageo-RT0603FKE0751K1L**  (mpn `RT0603FKE0751K1L`, value `51.1K`, fp `Resistor_SMD:R_0603_1608Metric`)
- `R4` [B] → **Yageo-RT0603FKE07100RL**  (mpn `RT0603FKE07100RL`, value `100`, fp `Resistor_SMD:R_0603_1608Metric`)
- `R5` [B] → **Yageo-RT0603FKE071KL**  (mpn `RT0603FKE071KL`, value `1K`, fp `Resistor_SMD:R_0603_1608Metric`)
- `R6` [B] → **Yageo-RT0603FKE07100RL**  (mpn `RT0603FKE07100RL`, value `100`, fp `Resistor_SMD:R_0603_1608Metric`)
- `R7` [B] → **Yageo-RT0603FKE0751K1L**  (mpn `RT0603FKE0751K1L`, value `51.1K`, fp `Resistor_SMD:R_0603_1608Metric`)
- `R8` [B] → **Yageo-RT0603FKE0751K1L**  (mpn `RT0603FKE0751K1L`, value `51.1K`, fp `Resistor_SMD:R_0603_1608Metric`)
- `R9` [B] → **Yageo-RT0603FKE071KL**  (mpn `RT0603FKE071KL`, value `1K`, fp `Resistor_SMD:R_0603_1608Metric`)

### TestPoint (19)
- `TP1` [A] → **Keystone-5017**  (mpn `5017`, value `Test Point`, fp `terra-test-points:TestPoint_Pad_3.43x1.78mm`)
- `TP10` [A] → **Keystone-5017**  (mpn `5017`, value `Test Point`, fp `terra-test-points:TestPoint_Pad_3.43x1.78mm`)
- `TP11` [A] → **Keystone-5017**  (mpn `5017`, value `Test Point`, fp `terra-test-points:TestPoint_Pad_3.43x1.78mm`)
- `TP12` [A] → **Keystone-5017**  (mpn `5017`, value `Test Point`, fp `terra-test-points:TestPoint_Pad_3.43x1.78mm`)
- `TP13` [A] → **Keystone-5017**  (mpn `5017`, value `Test Point`, fp `terra-test-points:TestPoint_Pad_3.43x1.78mm`)
- `TP14` [A] → **Keystone-5017**  (mpn `5017`, value `Test Point`, fp `terra-test-points:TestPoint_Pad_3.43x1.78mm`)
- `TP15` [A] → **Keystone-5017**  (mpn `5017`, value `Test Point`, fp `terra-test-points:TestPoint_Pad_3.43x1.78mm`)
- `TP16` [A] → **Keystone-5017**  (mpn `5017`, value `Test Point`, fp `terra-test-points:TestPoint_Pad_3.43x1.78mm`)
- `TP17` [A] → **Keystone-5017**  (mpn `5017`, value `Test Point`, fp `terra-test-points:TestPoint_Pad_3.43x1.78mm`)
- `TP18` [A] → **Keystone-5017**  (mpn `5017`, value `Test Point`, fp `terra-test-points:TestPoint_Pad_3.43x1.78mm`)
- `TP19` [A] → **Keystone-5017**  (mpn `5017`, value `Test Point`, fp `terra-test-points:TestPoint_Pad_3.43x1.78mm`)
- `TP2` [A] → **Keystone-5017**  (mpn `5017`, value `Test Point`, fp `terra-test-points:TestPoint_Pad_3.43x1.78mm`)
- `TP3` [A] → **Keystone-5017**  (mpn `5017`, value `Test Point`, fp `terra-test-points:TestPoint_Pad_3.43x1.78mm`)
- `TP4` [A] → **Keystone-5017**  (mpn `5017`, value `Test Point`, fp `terra-test-points:TestPoint_Pad_3.43x1.78mm`)
- `TP5` [A] → **Keystone-5017**  (mpn `5017`, value `Test Point`, fp `terra-test-points:TestPoint_Pad_3.43x1.78mm`)
- `TP6` [A] → **Keystone-5017**  (mpn `5017`, value `Test Point`, fp `terra-test-points:TestPoint_Pad_3.43x1.78mm`)
- `TP7` [A] → **Keystone-5017**  (mpn `5017`, value `Test Point`, fp `terra-test-points:TestPoint_Pad_3.43x1.78mm`)
- `TP8` [A] → **Keystone-5017**  (mpn `5017`, value `Test Point`, fp `terra-test-points:TestPoint_Pad_3.43x1.78mm`)
- `TP9` [A] → **Keystone-5017**  (mpn `5017`, value `Test Point`, fp `terra-test-points:TestPoint_Pad_3.43x1.78mm`)

### Transistor (5)
- `Q1` [A] → **Diodes, Inc.-DMP3099L**  (mpn `DMP3099L`, value `DMP3099L-7`, fp `Package_TO_SOT_SMD:SOT-23`)
- `Q2` [A] → **Diodes_Incorporated-MMBT3906**  (mpn `MMBT3906`, value `MMBT3906`, fp `Package_TO_SOT_SMD:SOT-23`)
- `Q4` [A] → **Diodes, Inc.-DMP3099L**  (mpn `DMP3099L`, value `DMP3099L-7`, fp `Package_TO_SOT_SMD:SOT-23`)
- `Q6` [A] → **Diodes_Incorporated-MMBT3906**  (mpn `MMBT3906`, value `MMBT3906`, fp `Package_TO_SOT_SMD:SOT-23`)
- `Q7` [A] → **Diodes, Inc.-DMP3099L**  (mpn `DMP3099L`, value `DMP3099L-7`, fp `Package_TO_SOT_SMD:SOT-23`)

## MANUAL (13) — symbol pin layout differs; convert by hand in GUI

- `C1` [A] mpn `EKYC250ELL392MK30S` → intended terra `Nippon_Chemi-Con-EKYC250ELL392MK30S`
- `D10` [A] mpn `SMF6.0A` → intended terra `Littelfuse-SMF6.0A`
- `D11` [A] mpn ` ESDA18-1K ` → intended terra `STMicroelectronics-ESDA18-1K`
- `D12` [A] mpn ` ESDA18-1K ` → intended terra `STMicroelectronics-ESDA18-1K`
- `D13` [A] mpn ` ESDA18-1K ` → intended terra `STMicroelectronics-ESDA18-1K`
- `D5` [A] mpn `SM712-02HTG` → intended terra `Littelfuse-SM712-02HTG`
- `D7` [A] mpn `SM712-02HTG` → intended terra `Littelfuse-SM712-02HTG`
- `D9` [A] mpn `SMF18A` → intended terra `Littelfuse-SMF18A`
- `Q3` [A] mpn `MMBT3904` → intended terra `NEXPERIA-MMBT3904`
- `Q5` [A] mpn `MMBT3904` → intended terra `NEXPERIA-MMBT3904`
- `Q8` [A] mpn `MMBT3904` → intended terra `NEXPERIA-MMBT3904`
- `Q9` [A] mpn `MMBT3904` → intended terra `NEXPERIA-MMBT3904`
- `U3` [A] mpn `OPB733TR` → intended terra `TT_Electronics-OPB733TR`

## LEAVE: {'C': 10, 'REVIEW': 1} (gaps / mounting holes / empty-MPN — not converted)