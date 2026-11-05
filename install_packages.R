# install_packages.R — run once:  source("install_packages.R")
pkgs <- c("ggplot2", "dplyr", "readr", "tidyr", "scales", "jsonlite")
new <- pkgs[!pkgs %in% rownames(installed.packages())]
if (length(new)) install.packages(new)
message("All EEGB R packages are installed.")
