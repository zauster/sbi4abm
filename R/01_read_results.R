library(conflicted)
library(data.table)
suppressMessages(library(here))
setwd(here::here())

result_dirs <- list.dirs("results", full.names = TRUE, recursive = FALSE)
input_dir <- result_dirs[1]

result_list <- list()
for(input_dir in result_dirs) {
  message("=> ", input_dir)

  ## get the sampled parameters
  samples_file <- file.path(input_dir, "samples.txt")
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
}
res_dt <- rbindlist(result_list)

res_dt[, table(embedding)]
res_dt[, table(network)]

library(ggplot2)

p1 <- ggplot(res_dt, aes(x = value)) +
  geom_density(aes(colour = method), linewidth = 1) +
  facet_wrap(~ variable)
p1

p2 <- ggplot(res_dt, aes(x = value)) +
  geom_density(aes(colour = embedding), linewidth = 1) +
  facet_grid(network ~ variable)
p2
