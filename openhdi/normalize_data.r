indicator.file <- "../data/indicator.csv"
dataset.file <- "../data/dataset.csv"
output.file <- "../data/dataset_normalized.csv"

indicator <- read.csv(indicator.file)
dataset <- read.csv(dataset.file)



for (ind.name in levels(indicator$name))
  {
    cat(ind.name, "\n")
    mask <- dataset$indicator_name == ind.name
    unnormalized <- dataset[mask, 'value']
    mask.nan <- !is.na(unnormalized)
    mmin <- min(unnormalized[mask.nan])
    rrange <- diff(range(unnormalized[mask.nan]))
    normalized <- rep(NA, length(unnormalized))
    if (indicator$good[ind.name == levels(indicator$name)])
      {
        normalized = (unnormalized - mmin) / rrange
      } else
      {
        normalized = 1 - (unnormalized - mmin) / rrange
      }

    dataset$normalized.value[mask] <- normalized
  }

write.csv(dataset, output.file)
