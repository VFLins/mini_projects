##### Coleta de dados mensais a partir dos servidores oficiais SIDRA
## recomendado manter codificação do documento em 'latin1'
meses <- seq(
  from =as.yearmon({Sys.Date() %>% year() - 6}),
  to =as.yearmon(Sys.Date()),
  by =1/12) %>%
  as.Date()

# dados do sidra
sidra <- list()
#sidra$date <- meses

# Desemprego
sidra$unemp <- get_sidra(
  6381,
  variable =4099,
  period ={meses %>% format("%Y%m")}
) %>% select(`Trimestre Móvel (Código)`, Valor) %>%
  setNames(c("meses", "unemp")) %>%
  mutate(meses =as.yearmon(meses, format ="%Y%m"))

# Inflacao INPC mensal
sidra$prec0 <- get_sidra(
  1736,
  variable =44,
  period ={meses %>% format("%Y%m")}
) %>% select(`Mês (Código)`, Valor) %>%
  setNames(c("meses", "prec0")) %>%
  mutate(meses =as.yearmon(meses, format ="%Y%m"))

# Inflacao IPCA acumulado 12 meses
sidra$infla <- get_sidra(
  1737,
  variable =c(2265,2266),
  period ={meses %>% format("%Y%m")}
) %>% select(`Mês (Código)`, Variável, Valor) %>%
  setNames(c("meses", "grupo", "preco")) %>%
  mutate(meses =as.yearmon(meses, format ="%Y%m")) %>%
  pivot_wider(names_from =grupo, values_from =preco)
dicio_infla <- names(sidra$infla[1, 2:ncol(sidra$infla)])
names(sidra$infla) <- c("meses", "inf12", "inf00")
names(dicio_infla) <- c("inf12", "inf00")

# Inflacao INPC mensal por grupo
sidra$preco <- get_sidra(
  api ="/t/7063/n1/all/v/44/p/all/c315/7170,7445,7486,7558,7625,7660,7712,7766,7786/d/v44%202"
) %>% select(`Mês (Código)`, `Geral, grupo, subgrupo, item e subitem`, Valor) %>%
  setNames(c("meses", "grupo", "preco")) %>%
  mutate(meses =as.yearmon(meses, format ="%Y%m")) %>%
  .[.$meses %in% as.yearmon(meses), ] %>%
  pivot_wider(names_from =grupo, values_from =preco)
dicio_preco <- names(sidra$preco[1, 2:ncol(sidra$preco)])
names(sidra$preco) <- c("meses", paste0("prec", 1:9))
names(dicio_preco) <- paste0("prec", 1:9)

for (i in 2:length(sidra)) {
  if (i <= 2) { sidram <- full_join(sidra[[i]], sidra[[I(i-1)]]) }
  else { sidram <- full_join(sidram, sidra[[i]]) }
}
rm(i)
