library(zoo)
library(tidyr)
library(dplyr)
library(sidrar)
library(ggplot2)
library(forecast)

ipca <- get_sidra(api="/t/1737/n1/all/v/63,2266/p/all/d/v63%202,v2266%2013") %>%
	.[,c("Mês (Código)", "Variável", "Valor")] %>%
	setNames(c("mes", "var", "val")) %>%
	pivot_wider(., id_cols=mes, names_from=var, values_from=val) %>%
	setNames(c("mes","var_percent","indice")) %>%
	mutate(mes=as.yearmon(mes, format="%Y%m"))

thisyear <- Sys.Date() %>% format("%Y-%m") %>% as.yearmon()
yearsago <- yearmon(thisyear-3)

mdl <- rwf(ipca$indice[ipca$mes >= yearmon(yearsago)], drift=F, h=6, biasadj=T)
autoplot(mdl) + labs(y="Índice IPCA", x=NULL, title="Previsão RW com drift") + theme_bw()

preds <- c(last(ipca$indice), mdl$mean)

var_preds <- c()
for (i in seq_along(preds)){
	if (i>1) {
		var_preds[i-1] <- (diff(preds[c(i-1, i)])/preds[i])*100}}
