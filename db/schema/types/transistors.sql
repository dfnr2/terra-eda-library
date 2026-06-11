-- db/schema/types/transistors.sql
    transistor_type TEXT,     -- npn | pnp | nmos | pmos | igbt | jfet | ...
    channels INTEGER,
    v_ce_ds_max TEXT,         -- Vce (BJT) / Vds (FET)
    i_c_d_max TEXT,           -- Ic / Id
    power_dissipation TEXT,
    hfe_typ TEXT,             -- BJT gain (null for FET)
    rds_on TEXT,              -- FET on-resistance (null for BJT)
    vgs_th TEXT,              -- FET threshold (null for BJT)
    transition_freq TEXT,     -- ft
    temp_junction_max TEXT    -- Tj max
