# theme_eegb.R — shared chart style for every EEGB R script.
#
# Usage (from the project root — open eegb.Rproj in RStudio first):
#   source("R/theme_eegb.R")
#   p <- ggplot(...) + theme_eegb()
#   save_fig(p, "s02", "f03")   # -> sessions/s02/figures/r/s02_f03.png

suppressPackageStartupMessages({
  library(ggplot2)
  library(scales)
})

# Lagos Business School deck palette (matches the slides and the Python style)
eegb <- c(navy = "#141B4D", teal = "#0B5E82", teal2 = "#1C7293", gold = "#D99A2B",
         rust = "#B5541A", slate = "#5C6B7A", ink = "#1A2233", light = "#F3F6F9",
         grid = "#E1E7EE", olive = "#8C8A4E", sky = "#7FB3C8")
eegb_palette <- unname(eegb[c("teal", "gold", "navy", "rust", "teal2", "olive", "sky", "slate")])

# Font: your system default works on Windows/Mac. If the naira sign shows as a box,
# set e.g. Sys.setenv(EEGB_FONT = "Arial") or "DejaVu Sans" before sourcing this file.
eegb_font <- Sys.getenv("EEGB_FONT", "")
if (nzchar(eegb_font)) {
  update_geom_defaults("text", list(family = eegb_font))
  update_geom_defaults("label", list(family = eegb_font))
}

theme_eegb <- function(base_size = 13) {
  theme_minimal(base_size = base_size, base_family = eegb_font) +
    theme(
      plot.title = element_text(face = "bold", colour = eegb[["navy"]], size = base_size + 3,
                                margin = margin(b = 10)),
      plot.title.position = "plot",
      plot.subtitle = element_text(colour = eegb[["slate"]], margin = margin(b = 10)),
      axis.title = element_text(colour = eegb[["ink"]]),
      axis.text = element_text(colour = eegb[["slate"]]),
      panel.grid.major = element_line(colour = eegb[["grid"]], linewidth = 0.4),
      panel.grid.minor = element_blank(),
      axis.line = element_line(colour = "#B8C2CE", linewidth = 0.4),
      legend.position = "top", legend.justification = "left",
      plot.background = element_rect(fill = "white", colour = NA)
    )
}
scale_colour_eegb <- function(...) scale_colour_manual(values = eegb_palette, ...)
scale_fill_eegb   <- function(...) scale_fill_manual(values = eegb_palette, ...)

# 12500 -> ₦12.5k ; 2500000 -> ₦2.5m
naira <- function(x) {
  ifelse(abs(x) >= 1e6, paste0("₦", format(round(x / 1e6, 1), nsmall = 1), "m"),
         ifelse(abs(x) >= 1e3, paste0("₦", round(x / 1e3), "k"), paste0("₦", round(x))))
}

save_fig <- function(p, session, fig_id, width = 10, height = 5.6) {
  out <- file.path("sessions", session, "figures", "r")
  dir.create(out, recursive = TRUE, showWarnings = FALSE)
  path <- file.path(out, paste0(session, "_", fig_id, ".png"))
  ggsave(path, p, width = width, height = height, dpi = 200, bg = "white")
  message("saved ", path)
  invisible(path)
}

# 2.5e9 -> $2.5bn
usd <- function(x) ifelse(abs(x) >= 1e9, paste0("$", round(x / 1e9, 1), "bn"),
                    ifelse(abs(x) >= 1e6, paste0("$", round(x / 1e6, 1), "m"), paste0("$", format(round(x), big.mark = ","))))
# values already in percent: 12.5 -> "12.5%"
pct <- function(x) paste0(x, "%")
eegb_caption <- "Source: EEGB stylised teaching data (data/). Not official statistics."
