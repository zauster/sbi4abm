library(conflicted)
library(data.table)
suppressMessages(library(here))
setwd(here::here())
library(ggplot2)
library(ggthemes)
library(configr) ## just for reading toml
library(toml) ## just for writing toml
library(stringr)
library(lubridate)

estimate_mode <- function(x) {
  d <- density(x)
  d$x[which.max(d$y)]
}

## result_basedir <- "results_methods_500x3_8var"
## result_basedir <- "results_allMethods_500x5_twoVar"
## result_basedir <- "results_artificial"
result_basedir <- "results_empirical"

result_dirs <- list.dirs(result_basedir,
                         full.names = TRUE, recursive = FALSE) |>
  str_subset("backup", negate = TRUE)
## result_dirs <- result_dirs[length(result_dirs)]
## input_dir <- result_dirs[length(result_dirs)]
print(result_dirs)

result_list <- list()
for(input_dir in result_dirs) {
  message("=> ", input_dir)

  ## get the sampled parameters
  samples_file <- file.path(input_dir, "samples.txt")
  if(file.exists(samples_file)) {
    tmp <- fread(samples_file)
    ## ## we just add the input_dir so that 'melt' does not complain
    ## setnames(tmp, paste0("V", str_pad(as.character(1:length(colnames(tmp))),
    ##                                   width = 2, side = "left", pad = "0")))
    tmp[, dir_name := input_dir]
    tmp <- melt(tmp, id.vars = c("dir_name"),
                variable.factor = FALSE)
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

## res_dt <- rbindlist(result_list)
res_dt <- rbindlist(result_list, fill = TRUE)
res_dt[, table(variable)]
res_dt[, table(nsims)]

## restrict samples to "meaningful" nsims
res_dt[, nsims := str_remove_all(nsims, "[:punct:]")]
res_dt[, c("niterations", "nbatches") := tstrsplit(nsims, "x", type.convert = TRUE)]
res_dt[, table(niterations)]
res_dt <- res_dt[niterations >= 500, ]

## get the 'true' values of the variables, if comparing artificial
## timeseries
toml_config_path <- file.path("/mnt/extData3/2023_OeNB_GeneticOptimisation_ABM/models/MultiIndustry_ABM/model_config.toml")
toml_config <- read.config(toml_config_path)

truevalues_dt <- fread(
"
variable, true_value
expectation_reaction_parameter, 0.1
consumption_propensity_income, 0.953
desired_real_output_inventory_ratio, 0.54
desired_intermediate_inputs_inventory_factor, 2.14
inflation_adj_parameter, 0.7
markup_reaction_parameter, 0.005
firm_order_market_weighting_parameter, 0.33
budget_adj_parameter, 0.5
unempl_react_parameter, 1.0
profit_retention_ratio_firms, 0.0
credit_supply_factor_assets, 1.5
credit_supply_factor_profits, 1.5
job_search_probability_employed, 0.1
financial_needs_buffer_factor, 1.1
investment_reaction_parameter, 0.5
", header = TRUE)

## Merge the 'true' values
res_dt <- merge(res_dt, truevalues_dt,
                by = "variable", all.x = TRUE)

## Make the variable descriptions a little more prettier
res_dt[, variable_desc_pretty := str_replace_all(variable, "_", " ") |>
           str_to_sentence()]

## Also create a better descriptor of the calibration run
res_dt[, calibration_time_msec := str_replace_all(dir_name,
                                            "results_empirical/", "") |>
       str_replace_all("\\.[0-9]+$", "")]
res_dt[, calibration_time := as.POSIXct(as.numeric(calibration_time_msec))]

res_dt <- res_dt[calibration_time >= "2024-12-20", ]

timestamps <- res_dt[, unique(calibration_time_msec)]
timestamp_ids <- c("twoMarkets", "singleMarket")
## timestamp_ids <- rep("twoMarkets", length = length(timestamps))
names(timestamp_ids) <- timestamps
## timestamps <- res_dt[, unique(calibration_time_msec)]
## res_dt[, calibration_indicator := ""]
res_dt[, calibration_indicator := str_replace_all(calibration_time_msec,
                                                  timestamp_ids)]

res_dt[, calibration_run_name := paste0(
           str_replace_all(as.character(calibration_time), c(":" = "", "-" = "", " " = "_")),
           "_", network, "_", calibration_indicator)]

## Compute mean, mode and median of the distributions
res_dt[, mean := mean(value),
       by = .(variable, calibration_run_name)]
res_dt[, mode := estimate_mode(round(value, digits = 4)),
       by = .(variable, calibration_run_name)]
res_dt[, median := median(value),
       by = .(variable, calibration_run_name)]

## Compute mean, mode and median of the distributions and save the
## found mode of the parameter samples as the calibrated parameter.
calibrated_parameters <- res_dt %>%
  .[, .(mode = round(estimate_mode(round(value, digits = 4)), digits = 4),
        mean = round(mean(value), digits = 4),
        median = round(median(value), digits = 4),
        cv = sd(value) / mean(value)
        ),
    keyby = .(variable, calibration_run_name)]
calibrated_parameters

## By default, write the values from the newest calibration run to
## file
calibrations_to_save_to_toml <-
  res_dt[calibration_time == max(calibration_time),
         unique(calibration_run_name)]
## res_dt[, unique(calibration_run_name)]
for(calibration_name in calibrations_to_save_to_toml) {
  message("=> ", calibration_name)
  calibrated_parameters_to_save <- calibrated_parameters[calibration_run_name == calibration_name, ]
  calibrated_values_config <- copy(toml_config)
  for(statistic in c("mode", "mean", "median")) {
    message("--> Writing .toml for statistic: ", statistic)
    for(parameter in calibrated_parameters_to_save$variable) {
      calibrated_values_config[[parameter]] <-
        calibrated_parameters_to_save[variable == parameter, get(statistic)]
    }
    ## Also set the calibration data name to a new value, so that we
    ## can easier call 00_runAllScripts with this model_config:
    calibrated_values_config[["calibrated_parameters"]] <-
      paste0("calibrated_model_parameters_", statistic, "_",
             calibration_name, ".RData")

    ## Create new filename and write .toml to disk:
    calibrated_toml_config <-
      file.path(dirname(toml_config_path),
                paste0("model_config_calibrated_",
                       statistic, "_", calibration_name, ".toml"))
    write_toml(calibrated_values_config,
               calibrated_toml_config)
  }
}


plot_width <- 7
plot_height <- 13

p1 <- ggplot(res_dt, aes(x = value))
if(result_basedir %like% "artificial") {
  p1 <- p1 + geom_vline(aes(xintercept = true_value), linewidth = 1,
                        colour = "lightgrey")
}
p1 <- p1 + geom_vline(aes(xintercept = mean), linewidth = 1,
                      colour = "green")
p1 <- p1 + geom_vline(aes(xintercept = median), linewidth = 1,
                      colour = "orange")
p1 <- p1 + geom_vline(aes(xintercept = mode), linewidth = 1,
                      colour = "brown")
p1 <- p1 + geom_density(aes(colour = factor(calibration_time)),
                        linewidth = 1) +
  facet_wrap(~ variable_desc_pretty, scales = "free") +
  xlab("") + ylab("") +
  theme_clean() +
  ggtitle(label = "",
          subtitle = "True value (if applicable, grey); mean (green), median (orange), mode (brown)") +
  scale_colour_ptol("Calibration run")
## p1

ggsave(plot = p1, height = plot_width, width = plot_height,
       filename = paste0("plots/", result_basedir, "_",
                         str_replace_all(as.Date(res_dt[, max(calibration_time)]),
                                         "-", ""),
                         "_hist1.png"))


##============================================================
## old:
## p_gru <- ggplot(res_dt[embedding == "gru", ], aes(x = value)) +
##   geom_vline(aes(xintercept = true_value), linewidth = 1, colour = "lightgrey") +
##   geom_density(aes(colour = network), linewidth = 1) +
##   facet_wrap( ~ variable, scales = "free") +
##   xlab("") + ylab("") +
##   theme_clean() +
##   theme(strip.text = element_text(size = 15)) +
##   scale_colour_ptol("Network")
## ## p_gru
## ggsave(plot = p_gru, width = 20, height = 11,
##        filename = paste0("plots/", result_basedir, "_gru_hist.png"))

## p2 <- ggplot(res_dt, aes(x = value)) +
##   geom_vline(aes(xintercept = true_value), linewidth = 1, colour = "lightgrey") +
##   geom_density(aes(colour = embedding), linewidth = 1) +
##   ## facet_grid(network ~ variable, scales = "free") +
##   facet_wrap( ~ network + variable, scales = "free") +
##   xlab("") + ylab("") +
##   theme_clean() +
##   scale_colour_ptol()
## p2
## ## ggsave(plot = p2, width = 20, height = 11,
## ##        filename = paste0("plots/", result_basedir, "_hist2.png"))

## p3 <- ggplot(res_dt, aes(x = value)) +
##   geom_vline(aes(xintercept = true_value), linewidth = 1, colour = "lightgrey") +
##   geom_density(aes(colour = network), linewidth = 1) +
##   ## facet_grid(embedding ~ variable, scales = "free") +
##   facet_wrap( ~ embedding + variable, scales = "free") +
##   xlab("") + ylab("") +
##   theme_clean() +
##   scale_colour_ptol()
## p3

