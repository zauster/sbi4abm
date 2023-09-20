library(conflicted)
library(data.table)
suppressMessages(library(here))
setwd(here::here())
library(ggplot2)

## result_basedir <- "results_allMethods_500x5"
result_basedir <- "results"

result_dirs <- list.dirs(result_basedir, full.names = TRUE, recursive = FALSE)
## result_dirs <- result_dirs[length(result_dirs)]
## input_dir <- result_dirs[length(result_dirs)]

result_list <- list()
for(input_dir in result_dirs) {
  message("=> ", input_dir)

  ## get the sampled parameters
  samples_file <- file.path(input_dir, "samples.txt")
  if(file.exists(samples_file)) {
  tmp <- fread(samples_file)
  ## we just add the input_dir so that 'melt' does not complain
  tmp[, dir_name := input_dir]
  tmp <- melt(tmp, id.vars = c("dir_name"))
  tmp[, dir_name := NULL]

  ## get the description of the algorithm that was run
  job_file <- file.path(input_dir, "this.job")
  job_desc <- fread(job_file, fill = TRUE, header = FALSE) |>
    setnames(c("parameter", "value"))
  job_desc[, dir_name := input_dir]
  job_desc_wide <- dcast(job_desc, dir_name ~ parameter)
  job_desc_wide[, c("network", "embedding") := tstrsplit(method, "_")]

  ## paste samples and configuration together
  tmp_full <- cbind(tmp, job_desc_wide)

  ## ... and save
  result_list[[input_dir]] = tmp_full
  } else {
    warning("=> Sample file does not exist: ", input_dir)
  }
}
res_dt <- rbindlist(result_list)

res_dt[, table(embedding)]
res_dt[, table(network)]
res_dt[, table(method)]
res_dt[, table(nsims)]
## res_dt[method == "resnet_gru", table(dir_name)]

truevalues_dt <- data.table(variable = c("V1", "V2"),
                            true_value = c(0.25, 0.001))
res_dt <- merge(res_dt, truevalues_dt,
                by = "variable")


p1 <- ggplot(res_dt, aes(x = value)) +
  geom_vline(aes(xintercept = true_value), linewidth = 1, colour = "lightgrey") +
  geom_density(aes(colour = method), linewidth = 1) +
  facet_wrap(~ variable, scales = "free")
p1

p2 <- ggplot(res_dt, aes(x = value)) +
  geom_vline(aes(xintercept = true_value), linewidth = 1, colour = "lightgrey") +
  geom_density(aes(colour = embedding), linewidth = 1) +
  facet_grid(network ~ variable, scales = "free")
p2

p3 <- ggplot(res_dt, aes(x = value)) +
  geom_vline(aes(xintercept = true_value), linewidth = 1, colour = "lightgrey") +
  geom_density(aes(colour = network), linewidth = 1) +
  facet_grid(embedding ~ variable, scales = "free")
p3
