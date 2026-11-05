# run_all.R — runs every R figure script, lab and starter. From the project root:  Rscript run_all.R
fails <- character()
for (f in sort(Sys.glob("sessions/s*/R/*.R"))) {
  message("running ", f)
  ok <- tryCatch({ source(f, local = new.env()); TRUE }, error = function(e) { message("  ERROR: ", conditionMessage(e)); FALSE })
  if (!ok) fails <- c(fails, f)
}
if (length(fails)) message("failed: ", paste(fails, collapse = ", ")) else message("all R scripts ran cleanly")
