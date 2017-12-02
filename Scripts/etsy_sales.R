
library(tidyverse)
library(zoo)
library(readxl)
library(lubridate)
library(lucr)

setwd("D:/Google Drive/EarthArtAustralia/")


# Etsy sales ----------------------------------------------------------------------------

# Read in all files
soldorders_df = list.files(path = "Donations and costs/",
                        pattern ="EtsySoldOrders*",
                        full.names = TRUE) %>% 
  
  # Read in each individually and merge output
  map(read_csv) %>%
  reduce(bind_rows) %>% 
  as.tbl() %>% 
  
  # Convert to date-time
  mutate(date = as.Date(`Sale Date`, format = "%m/%d/%y")) %>% 
  arrange(date) %>% 
  
  # Add missing dates and summarise sales/revenue/profit by date
  complete(date = full_seq(date, 1)) %>%
  group_by(date) %>% 
  summarise(orders = sum(!is.na(`Number of Items`)),
            sales = sum(`Number of Items`, na.rm = TRUE),
            revenue = sum(`Order Net`, na.rm = TRUE))


# Etsy deposits ----------------------------------------------------------------------------

# Read in all files
etsydeposits_df = list.files(path = "Donations and costs/",
                           pattern ="EtsyDeposits*",
                           full.names = TRUE) %>% 
  
  # Read in each individually and merge output
  map(read_csv) %>%
  reduce(bind_rows) %>% 
  as.tbl() %>% 
  
  # Convert to date-time
  mutate(date = as.Date(Date, format = "%B %d, %Y")) %>% 
  arrange(date) %>% 
  
  # Add missing dates and summarise sales/revenue/profit by date
  select(date = Date, amount = Amount) %>% 
  summarise(amount = sum(amount))


# Etsy fees ----------------------------------------------------------------------------

statements_df = list.files(path = "Donations and costs/",
                           pattern ="etsy_statement*",
                           full.names = TRUE) %>% 
  
  # Read in each individually and merge output
  map(read_csv) %>%
  reduce(bind_rows) %>% 
  as.tbl() %>% 
  
  # Convert to date-time
  mutate(date = as.Date(Date, format = "%d/%m/%Y")) %>% 
  arrange(date) %>% 
  
  # Add temporary ID to allow spreading and select columns
  filter(Activity != "payment") %>% 
  mutate(id=1:n()) %>%
  select(id, date, Activity, Fees) %>% 
  
  # Convert to long format
  group_by(date) %>%
  spread(key=Activity, value=Fees, fill = 0) %>% 
  
  # Sum all fees per day
  group_by(date) %>% 
  summarise_all(sum) %>% 

  # Sum across all variables to get total fees
  mutate(etsy_fees = rowSums(select(., -date, -id))) %>% 
  select(-id)


# Prinful costs -----------------------------------------------------------------------

printful_df = list.files(path = "Donations and costs/",
                           pattern ="printful*",
                           full.names = TRUE) %>% 
  
  # Read in each individually and merge output
  map(read_excel, sheet = 2, skip = 2) %>%
  reduce(bind_rows) %>% 
  as.tbl() %>% 
  
  # Remove summary row
  filter(Date !=  "Total paid:") %>% 
  
  # Convert to date-time
  mutate(date = as.Date(Date, format = "%B %d, %Y")) %>% 
  arrange(date) %>% 
  
  # Convert string to value
  mutate(cost = as.numeric(gsub(pattern = "\\$", replacement="", x = Total))) %>% 

  # Select
  select(date, cost) %>% 

  # Sum all fees per day
  group_by(date) %>% 
  summarise(printful_cost = sum(cost))

# Convert currency
currency_rates = historic_currency(printful_df$date, currency = "USD", key = "875f48ef191c4f73842e2fc4147d74e6")
printful_df$printful_cost = printful_df$printful_cost * unlist(lapply(currency_rates, function (x) x$rates$AUD))


# Join all ---------------------------------------------------------------------------

dow = c("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")

combined_df = left_join(soldorders_df, statements_df) %>% 
              left_join(printful_df) %>% 
  
  # Fix zeroes
  mutate(etsy_fees = ifelse(is.na(etsy_fees), 0, etsy_fees),
         printful_cost = ifelse(is.na(printful_cost), 0, printful_cost),
         expenses = etsy_fees + printful_cost) %>% 
  
  # Add metadata
  mutate(day = factor(strftime(date,'%A'), levels = dow),
         dayofyear = yday(date),
         dayofmonth = mday(date),
         month = factor(strftime(date,'%B'), levels = month.name),
         year = factor(strftime(date,'%Y'))) %>% 
  
  
  # Compute stats
  mutate(profit = revenue - expenses,
         salesperorder = sales / orders,
         
         # Rolling 30 day stats
         sales_30day = rollapplyr(sales, 30, sum, na.rm = TRUE, partial=TRUE),
         orders_30day = rollapplyr(orders, 30, sum, na.rm = TRUE, partial=TRUE),
         revenue_30day = rollapplyr(revenue, 30, sum, na.rm = TRUE, partial=TRUE),
         expenses_30day = rollapplyr(expenses, 30, sum, na.rm = TRUE, partial=TRUE),
         
         # Derived 30 day stats
         profit_30day = revenue_30day - expenses_30day,
         ratioprofitrev_30day = profit_30day / revenue_30day,
         profitpersale_30day = profit_30day / sales_30day,
         salesperorder_30day = sales_30day / orders_30day,
         yearlyequiv_30day = 365.25 * (profit_30day / 30))



# Plot -------------------------------------------------------------------------------

# Summary stats
combined_df %>% 
  summarise(orders = sum(orders),
            sales = sum(sales),
            revenue = sum(revenue),
            expenses = sum(expenses),
            profit = sum(profit))

# Last 30 days
# Profit by day of week
combined_df %>% 
  tail(n=30) %>% 
  ggplot() + geom_bar(aes(x = date, y = profit), stat = "identity") + theme_minimal() +
  scale_x_date("Date", date_breaks = "1 day", date_labels = "%d") 


# Last 30 days
# Sales by day of week
combined_df %>% 
  tail(n=30) %>% 
  ggplot() + geom_bar(aes(x = date, y = orders), stat = "identity") + theme_minimal() +
  scale_x_date("Date", date_breaks = "1 day", date_labels = "%d") 



# Yearly equivelent
combined_df %>% 
  mutate(yearlyequiv_ave = mean(yearlyequiv_30day)) %>% 
ggplot() + 
  geom_line(aes(x=date, y=yearlyequiv_30day)) + theme_minimal() +
  geom_hline(aes(yintercept = yearlyequiv_ave), color = "red") +
  geom_text(aes(y = yearlyequiv_ave*1.1, x = as.Date("2016-5-01"), 
                label = paste0("$", round(yearlyequiv_ave, -2))), color = "red", size = 3.5) +
  scale_x_date("Date", date_labels = "%b\n%y", date_breaks = "1 month") +
  scale_y_continuous(labels = scales::dollar, breaks = seq(0, 100000, 5000))

# Revenue and expenses
ggplot(data = combined_df) + 
  geom_line(aes(x=date, y=revenue_30day)) + 
  geom_line(aes(x=date, y=expenses_30day), color ="red") + theme_minimal() +
  scale_x_date("Date", date_labels = "%b\n%y", date_breaks = "1 month") +
  scale_y_continuous(labels = scales::dollar, breaks = seq(0, 100000, 1000))  

# Ratio of profit to revenue
ggplot(data = combined_df) + 
  geom_line(aes(x=date, y=ratioprofitrev_30day)) + theme_minimal() +
  scale_x_date("Date", date_labels = "%b\n%y", date_breaks = "1 month") +
  coord_cartesian(ylim = c(0, 1)) 

# Profits per sale
ggplot(data = combined_df) + 
  geom_line(aes(x=date, y=profitpersale_30day)) + theme_minimal() +
  scale_x_date("Date", date_labels = "%b\n%y", date_breaks = "1 month") +
  scale_y_continuous(labels = scales::dollar, breaks = seq(-10, 50, 1)) +
  coord_cartesian(ylim = c(0, max(combined_df$profitpersale_30day))) 

# Sales per order
ggplot(data = combined_df) + 
  geom_line(aes(x=date, y=salesperorder_30day)) + theme_minimal() +
  scale_x_date("Date", date_labels = "%b\n%y", date_breaks = "1 month")  



# Year by year, profit
combined_df %>% 
  mutate(date = as.Date(paste("2012", month(date),mday(date), sep = "-"))) %>% 
  ggplot() + 
    geom_line(aes(x=date, y=profit_30day, color = year, group = year)) + theme_minimal() +
    scale_x_date("Date", date_labels = "%b", date_breaks = "1 month") +
    scale_y_continuous(labels = scales::dollar, breaks = seq(0, 100000, 1000))  

# Year by year, sales
combined_df %>% 
  mutate(date = as.Date(paste("2012", month(date), mday(date), sep = "-"))) %>% 
  ggplot() + 
  geom_line(aes(x=date, y=sales_30day, color = year, group = year)) + theme_minimal() +
  scale_x_date("Date", date_labels = "%b", date_breaks = "1 month")

# Year by year, sales per order
combined_df %>% 
  mutate(date = as.Date(paste("2012", month(date), mday(date), sep = "-"))) %>% 
  ggplot() + 
  geom_line(aes(x=date, y=salesperorder_30day, color = year, group = year)) + theme_minimal() +
  scale_x_date("Date", date_labels = "%b", date_breaks = "1 month")



# Profit by day of week
combined_df %>% 
  group_by(day) %>% 
  summarise(profit = quantile(profit, 0.75)) %>% 
  ggplot() + geom_bar(aes(x = day, y = profit), stat = "identity") + theme_minimal() +
  scale_y_continuous(labels = scales::dollar, breaks = seq(0, 100, 10))  

# Sales by day of week
combined_df %>% 
  group_by(day) %>% 
  summarise(sales = quantile(sales, 0.75)) %>% 
  ggplot() + geom_bar(aes(x = day, y = sales), stat = "identity") + theme_minimal() 



# Cost breakdown
cost_df = combined_df %>% 
  mutate(GST = `GST credit` + GST, 
         listing = listing + `private listing` + `multi-quantity`, 
         transaction = transaction + `transaction credit`,
         `auto-renew sold` = `auto-renew sold` + `renew sold` ) %>% 
  select(date, `auto-renew sold`:GST, listing, `Promoted Listings`:`renew expired`,  transaction, printful_cost) %>% 
  gather(cost, value, -date) %>% 
  mutate(value = ifelse(is.na(value), 0, value), 
         cost = factor(cost, levels =rev(c("renew expired", 
                                           "Google Shopping Ads", 
                                           "renew", 
                                           "listing", 
                                           "GST", 
                                           "auto-renew sold", 
                                           "transaction", 
                                           "Promoted Listings", 
                                           "printful_cost")))) %>% 
  group_by(cost) %>% 
  arrange(date) %>% 
  mutate(value = rollapplyr(value, 30, sum, na.rm = TRUE, partial=TRUE))

# Cost stacked
ggplot(data = cost_df, aes(x = date, y = value)) +
  geom_area(aes(colour = cost, fill= cost), position = 'stack') +
  scale_fill_brewer(palette = "Paired") +
  scale_color_brewer(palette = "Paired") + theme_minimal() +
  scale_y_continuous(labels = scales::dollar, breaks = seq(0, 10000, 500)) +
  scale_x_date("Date", date_labels = "%b\n%y", date_breaks = "1 month")

# Cost percent
ggplot(data = cost_df, aes(x = date, y = value)) +
  geom_area(aes(colour = cost, fill= cost), position = 'fill') +
  scale_fill_brewer(palette = "Paired") +
  scale_color_brewer(palette = "Paired") + theme_minimal() +
  scale_x_date("Date", date_labels = "%b\n%y", date_breaks = "1 month")


