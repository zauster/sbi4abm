library(conflicted)
library(data.table)
suppressMessages(library(here))
setwd(here::here())
library(ggplot2)
library(ggthemes)
library(configr)

## result_basedir <- "results_methods_500x3_8var"
## result_basedir <- "results_allMethods_500x5_twoVar"
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
    warning("=> Sample file does not exist: ignoring directory ", input_dir)
  }
}

res_dt <- rbindlist(result_list)

## truevalues_dt <- data.table(variable = c("V1", "V2"),
##                             variable_desc = c("expectation reaction parameter",
##                                               "markup reaction parameter"),
##                             true_value = c(0.25, 0.001))

true_toml_config <- file.path("/mnt/extData3/2023_OeNB_GeneticOptimisation_ABM/models/MultiIndustry_ABM/model_config_5industries.toml")
truevalues_toml <- read.config(true_toml_config)

truevalues_dt <- data.table(variable = paste0("V", 1:6),
                            variable_desc = c("expectation_reaction_parameter",
                                              "inflation_adj_parameter",
                                              "financial_needs_buffer_factor",
                                              "markup_reaction_parameter",
                                              "firm_order_market_weighting_parameter",
                                              "job_search_probability_employed"),
                            true_value = c(0.1, 0.75, 1.1, 0.005, 0.33, 0.1))

## truevalues_toml[truevalues_dt$variable_desc]

res_dt <- merge(res_dt, truevalues_dt,
                by = "variable")


plot_width <- 7
plot_height <- 13

p1 <- ggplot(res_dt, aes(x = value)) +
  geom_vline(aes(xintercept = true_value), linewidth = 1, colour = "lightgrey") +
  geom_density(aes(colour = method), linewidth = 1) +
  facet_wrap(~ variable_desc, scales = "free") +
  xlab("") + ylab("") +
  theme_clean() +
  scale_colour_ptol()
p1
## ggsave(plot = p1, height = plot_width, width = plot_height,
##        filename = paste0("plots/", result_basedir, "_hist1.png"))

## p_gru <- ggplot(res_dt[embedding == "gru", ], aes(x = value)) +
##   geom_vline(aes(xintercept = true_value), linewidth = 1, colour = "lightgrey") +
##   geom_density(aes(colour = network), linewidth = 1) +
##   facet_wrap( ~ variable_desc, scales = "free") +
##   xlab("") + ylab("") +
##   theme_clean() +
##   theme(strip.text = element_text(size = 15)) +
##   scale_colour_ptol("Network")
## ## p_gru
## ggsave(plot = p_gru, width = 20, height = 11,
##        filename = paste0("plots/", result_basedir, "_gru_hist.png"))




##============================================================
## old:
## p2 <- ggplot(res_dt, aes(x = value)) +
##   geom_vline(aes(xintercept = true_value), linewidth = 1, colour = "lightgrey") +
##   geom_density(aes(colour = embedding), linewidth = 1) +
##   ## facet_grid(network ~ variable_desc, scales = "free") +
##   facet_wrap( ~ network + variable_desc, scales = "free") +
##   xlab("") + ylab("") +
##   theme_clean() +
##   scale_colour_ptol()
## p2
## ## ggsave(plot = p2, width = 20, height = 11,
## ##        filename = paste0("plots/", result_basedir, "_hist2.png"))

## p3 <- ggplot(res_dt, aes(x = value)) +
##   geom_vline(aes(xintercept = true_value), linewidth = 1, colour = "lightgrey") +
##   geom_density(aes(colour = network), linewidth = 1) +
##   ## facet_grid(embedding ~ variable_desc, scales = "free") +
##   facet_wrap( ~ embedding + variable_desc, scales = "free") +
##   xlab("") + ylab("") +
##   theme_clean() +
##   scale_colour_ptol()
## p3
