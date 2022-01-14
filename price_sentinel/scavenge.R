library(rvest)
library(tidyverse)
library(reticulate)

product_page <- "https://www.amazon.com.br/Headset-HyperX-Stinger-Nintendo-Switch/dp/B07BB3PYD8?ref_=Oct_d_obs_d_16253414011&pd_rd_w=7Gour&pf_rd_p=bb714210-6eec-49aa-acaf-70d6e1f0ef4d&pf_rd_r=GCPAYDWMNF4P76CNF7BY&pd_rd_r=689a07c5-0923-4c50-9b3e-607ff66ffd85&pd_rd_wg=xzJV9&pd_rd_i=B07BB3PYD8" 
currency_symbol <- "R$"

price <- read_html(product_page) %>% html_elements("input") %>%
  html_attr("data-base-product-price") %>% na.omit() %>% as.character() %>%
  str_replace(",", ".")
  
View(price)