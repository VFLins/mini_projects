##### Coleta de dados trimestrais a partir dos servidores oficiais SIDRA
## recomendado manter codifica��o do documento em 'latin1'
trimestres <- seq(
  from =as.yearqtr({Sys.Date() %>% year() - 6}),
  to =as.yearqtr(Sys.Date()),
  by =1/4) %>%
  gsub(" Q", "0", .)

sidra <- list()
#sidra$trimestre <- trimestres

# Valor adicionado total, agro, industria, e servi�os, respectivamente
sidra$vAdic <- get_sidra(
  1846,
  period =trimestres) %>%
  select(c("Trimestre (C�digo)", "Setores e subsetores (C�digo)", "Valor")) %>%
    setNames(c("trimestre", "setores", "valor")) %>%
    .[.$setores %in% c(90705, 90687, 90691, 90696), ] %>%
    mutate(setores =paste0("v", setores), trimestre =as.yearqtr(trimestre, format ="%Y%q")) %>%
    pivot_wider(names_from =setores, values_from =valor) %>%
    select(c(trimestre, v90705, v90687, v90691, v90696)) %>%
    setNames(c("trimestre", "vAdic_total", "vAdic_agro", "vAdic_indu", "vAdic_serv"))

# Valor adicionado a pre�os de 1995 total, agro, industria, e servi�os, respectivamente
sidra$vAdi2 <- get_sidra(
  6612,
  period =trimestres
) %>%
  select(c("Trimestre (C�digo)", "Setores e subsetores (C�digo)", "Valor")) %>%
  setNames(c("trimestre", "setores", "valor")) %>%
  .[.$setores %in% c(90705, 90687, 90691, 90696), ] %>%
  mutate(setores =paste0("v", setores), trimestre =as.yearqtr(trimestre, format ="%Y%q")) %>%
  pivot_wider(names_from =setores, values_from =valor) %>%
  select(c(trimestre, v90705, v90687, v90691, v90696)) %>%
  setNames(c("trimestre", "vAdi2_total", "vAdi2_agro", "vAdi2_indu", "vAdi2_serv"))

# Popula��o empregada
sidra$popEm <- get_sidra(
  4092,
  period =trimestres,
  variable =1641) %>%
  select(
    c("Trimestre (C�digo)",
    "Condi��o em rela��o � for�a de trabalho e condi��o de ocupa��o (C�digo)",
    "Valor")
  ) %>%
  setNames(c("trimestre", "setores", "popEm")) %>%
  subset(setores ==32387) %>%
  select(trimestre, popEm) %>%
  mutate(trimestre =as.yearqtr(trimestre, format ="%Y%q"))

sidra$reMed <-  get_sidra(5431, variable =5931, period =trimestres) %>% 
  select(c("Trimestre (C�digo)", "N�vel de instru��o", "N�vel de instru��o (C�digo)", "Valor")) %>%
  setNames(c("trimestre", "inst_nm", "inst_cd", "reMed")) %>%
  .[.$inst_cd %in% c("120704", "120706", "11628", "11630", "11632"), ] %>%
  select(-inst_cd) %>%
  pivot_wider(names_from =inst_nm, values_from =reMed, id_cols =trimestre) %>%
  mutate(trimestre =as.yearqtr(trimestre, format ="%Y%q"))
dicio_reMed <- names(sidra$reMed[1, 2:ncol(sidra$reMed)])
names(sidra$reMed) <- c("trimestre", paste0("reMe", 0:4))
names(dicio_reMed) <- paste0("reMe", 0:4)

for (i in 2:length(sidra)) {
  if (i <= 2) { sidrat <- full_join(sidra[[i]], sidra[[I(i-1)]]) }
  else { sidrat <- full_join(sidrat, sidra[[i]]) }}
rm(i)

