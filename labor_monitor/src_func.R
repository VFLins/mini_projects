### Fun��es personalizadas usadas no projeto

# transforma dados mensais em trimestrais somando os dados agregados
qtrlize <- function(x, func ="sum") {
  errorCondition(
    "x must be of type 'double', or coercible to this format.", 
    call =!{typeof(x) %in% c("logical", "double", "integer")})
  x <- as.double(x)
  
  n <- seq(3, length(x), by =3)
  if (n[length(n)] < length(x)) { n[length(n)+1] <- length(x) }
  
  output <- c()
  a =1
  if (func =="sum") {
    for (i in n) {
      output[a] <- sum(x[I(i-(2-{i %% 3})):i])
      a =a+1
    }
  } else if (func =="mean") {
    for (i in n) {
      output[a] <- mean(x[I(i-(2-{i %% 3})):i])
      a =a+1
    }
  } else if (func =="last") {
    for (i in n) {
      output[a] <- x[i]
      a =a+1
    }
  } else if (func =="first") {
    for (i in n) {
      output[a] <- x[I(i-2)]
      a =a+1
    }
  }
  output
}

# Simplesmente calcula varia��es percentuais
percentvar <- function(x) {diff(x)/x[-length(x)]}

# C�lculo da equa��o de fisher para juros real
#https://investimentoss.files.wordpress.com/2014/02/3.jpg
fisher_gir <- function(pi, ir) {
  gir = {
    ( (1+ir)/(1+pi) )-1
  }
  gir
}
