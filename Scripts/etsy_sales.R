
<<<<<<< Updated upstream
=======
library(rvest)
>>>>>>> Stashed changes
library(tidyverse)
library(zoo)
library(readxl)
library(lubridate)
library(lucr)
<<<<<<< Updated upstream

setwd("D:/Google Drive/EarthArtAustralia/")
=======
library(ggthemes)

setwd("C:/Users/Robbi/Google Drive/EarthArtAustralia")

# Owed for conservation: 
# sum(combined_df[579:636, "profit"])  # from Nov 17 2017 to Jan 17 2018 = 4618*0.1
>>>>>>> Stashed changes


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
  
<<<<<<< Updated upstream
=======
  # Fix adjusted amount
  mutate(`Order Net` = ifelse(!is.na(`Adjusted Net Order Amount`) & 
                              `Adjusted Net Order Amount` > 0,
                              `Adjusted Net Order Amount`, `Order Net`)) %>% 
  
>>>>>>> Stashed changes
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
  
<<<<<<< Updated upstream
=======
  # Coarse adjustment for USD
  mutate(Fees = Fees * 1.32) %>% 
  
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
=======

  # Remove false results
  grep(pattern ="~\\$", ., value = TRUE, invert = TRUE) %>% 
>>>>>>> Stashed changes
  
  # Read in each individually and merge output
  map(read_excel, sheet = 2, skip = 2) %>%
  reduce(bind_rows) %>% 
  as.tbl() %>% 
  
  # Remove summary row
  filter(Date !=  "Total paid:") %>% 
  
  # Convert to date-time
  mutate(date = as.Date(Date, format = "%B %d, %Y")) %>% 
  arrange(date) %>% 
  
<<<<<<< Updated upstream
  # Convert string to value
  mutate(cost = as.numeric(gsub(pattern = "\\$", replacement="", x = Total))) %>% 
=======
  # Convert string to value and add 3% currency conversion fee
  mutate(cost = as.numeric(gsub(pattern = "\\$", replacement="", x = Total)),
         cost = cost * 1.03) %>% 
>>>>>>> Stashed changes

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
         
<<<<<<< Updated upstream
=======
         # Rolling yearly stats
         revenue_1year = rollapplyr(revenue, 365, sum, na.rm = TRUE, partial=TRUE),
         profit_1year = rollapplyr(profit, 365, sum, na.rm = TRUE, partial=TRUE),
         expenses_1year = rollapplyr(expenses, 365, sum, na.rm = TRUE, partial=TRUE),
         
>>>>>>> Stashed changes
         # Derived 30 day stats
         profit_30day = revenue_30day - expenses_30day,
         ratioprofitrev_30day = profit_30day / revenue_30day,
         profitpersale_30day = profit_30day / sales_30day,
<<<<<<< Updated upstream
         salesperorder_30day = sales_30day / orders_30day,
         yearlyequiv_30day = 365.25 * (profit_30day / 30))
=======
         profitperorder_30day = profit_30day / orders_30day,
         revenueperorder_30day = revenue_30day / orders_30day,
         salesperorder_30day = sales_30day / orders_30day,
         
         # Annualised statistics
         revenue_annualised = 365.25 * (revenue_30day / 30),
         expenses_annualised = 365.25 * (expenses_30day / 30),
         profit_annualised = 365.25 * (profit_30day / 30))
>>>>>>> Stashed changes



# Plot -------------------------------------------------------------------------------

<<<<<<< Updated upstream
# Summary stats
=======
# Summary stats all time
>>>>>>> Stashed changes
combined_df %>% 
  summarise(orders = sum(orders),
            sales = sum(sales),
            revenue = sum(revenue),
            expenses = sum(expenses),
            profit = sum(profit))

<<<<<<< Updated upstream
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
=======
# Summary stats last 30 days
combined_df %>% 
  tail(n=30) %>% 
  summarise(orders = sum(orders),
            sales = sum(sales),
            revenue = sum(revenue),
            expenses = sum(expenses),
            profit = sum(profit))

# Summary stats last 7 days
combined_df %>% 
  tail(n=7) %>% 
  summarise(orders = sum(orders),
            sales = sum(sales),
            revenue = sum(revenue),
            expenses = sum(expenses),
            profit = sum(profit))

# Last 30 days, profit
combined_df %>% 
  tail(n=30) %>% 
  ggplot() + geom_bar(aes(x = date, y = profit), stat = "identity") + 
  scale_y_continuous(labels = scales::dollar, expand = c(0,0)) +
  scale_x_date("Date", date_breaks = "1 day", date_labels = "%d", expand = c(0,0))  +
  theme_tufte(base_family = "sans")  

# Last 30 days, sales
combined_df %>% 
  tail(n=30) %>% 
  ggplot() + geom_bar(aes(x = date, y = sales), stat = "identity") + 
  scale_x_date("Date", date_breaks = "1 day", date_labels = "%d", expand = c(0,0))  +
  scale_y_continuous(expand = c(0,0)) +
  theme_tufte(base_family = "sans")  

# Recent values
combined_df %>% 
  tail(n=7) %>% 
  select(date, orders, sales, revenue, expenses, profit)

# Ratio of profit to revenue
ggplot(data = combined_df) + 
  geom_line(aes(x=date, y=ratioprofitrev_30day)) + 
  scale_x_date("Date", date_labels = "%b\n%y", date_breaks = "1 month", expand = c(0,0)) +
  scale_y_continuous(expand = c(0,0)) +
  coord_cartesian(ylim = c(0, 1))  +
  theme_tufte(base_family = "sans")  


# Year by year, profit annualised
combined_df %>% 
  group_by(year) %>% 
  mutate(profit_annualised_yearlyave = mean(profit_annualised),
         date = as.Date(paste("2012", month(date), mday(date), sep = "-"))) %>% 
  ggplot() + 
  geom_line(aes(x=date, y=profit_annualised, color = year, group = year)) + 
  geom_hline(aes(yintercept = profit_annualised_yearlyave, color = year), alpha = 0.3) +
  scale_x_date("Date", date_labels = "%b", date_breaks = "1 month", expand = c(0,0)) +
  scale_y_continuous(labels = scales::dollar, breaks = seq(0, 100000, 5000), expand = c(0,0)) +
  theme_tufte(base_family = "sans") 

# Year by year, revenue annualised
combined_df %>% 
  group_by(year) %>% 
  mutate(revenue_annualised_yearlyave = mean(revenue_annualised),
         date = as.Date(paste("2012", month(date), mday(date), sep = "-"))) %>% 
  ggplot() + 
  geom_line(aes(x=date, y=revenue_annualised, color = year, group = year)) + 
  geom_hline(aes(yintercept = revenue_annualised_yearlyave, color = year), alpha = 0.3) +
  scale_x_date("Date", date_labels = "%b", date_breaks = "1 month", expand = c(0,0)) +
  scale_y_continuous(labels = scales::dollar, breaks = seq(0, 100000, 10000), expand = c(0,0)) +
  theme_tufte(base_family = "sans") 

# Year by year, expenses annualised
combined_df %>% 
  group_by(year) %>% 
  mutate(expenses_annualised_yearlyave = mean(expenses_annualised),
         date = as.Date(paste("2012", month(date), mday(date), sep = "-"))) %>% 
  ggplot() + 
  geom_line(aes(x=date, y=expenses_annualised, color = year, group = year)) + 
  geom_hline(aes(yintercept = expenses_annualised_yearlyave, color = year), alpha = 0.3) +
  scale_x_date("Date", date_labels = "%b", date_breaks = "1 month", expand = c(0,0)) +
  scale_y_continuous(labels = scales::dollar, breaks = seq(0, 100000, 5000), expand = c(0,0)) +
  theme_tufte(base_family = "sans") 



# Year by year, orders per day
combined_df %>% 
  group_by(year) %>% 
  mutate(orders_yearlyave = mean(orders_30day) / 30,
         date = as.Date(paste("2012", month(date), mday(date), sep = "-"))) %>% 
  ggplot() + 
  geom_line(aes(x=date, y=orders_30day / 30, color = year, group = year)) + 
  geom_hline(aes(yintercept = orders_yearlyave, color = year), alpha = 0.3) +
  scale_x_date("Date", date_labels = "%b", date_breaks = "1 month", expand = c(0,0)) + 
  scale_y_continuous(expand = c(0,0)) +
  theme_tufte(base_family = "sans")

# Year by year, sales per day
combined_df %>% 
  group_by(year) %>% 
  mutate(sales_yearlyave = mean(sales_30day) / 30,
         date = as.Date(paste("2012", month(date), mday(date), sep = "-"))) %>% 
  ggplot() + 
  geom_line(aes(x=date, y=sales_30day / 30, color = year, group = year)) + 
  geom_hline(aes(yintercept = sales_yearlyave, color = year), alpha = 0.3) +
  scale_x_date("Date", date_labels = "%b", date_breaks = "1 month", expand = c(0,0)) + 
  scale_y_continuous(expand = c(0,0)) +
  theme_tufte(base_family = "sans")

# Year by year, sales per order
combined_df %>% 
  group_by(year) %>% 
  mutate(salesperorder_yearlyave = mean(salesperorder_30day),
         date = as.Date(paste("2012", month(date), mday(date), sep = "-"))) %>% 
  ggplot() + 
  geom_line(aes(x=date, y=salesperorder_30day, color = year, group = year)) + 
  geom_hline(aes(yintercept = salesperorder_yearlyave, color = year), alpha = 0.3) +
  scale_x_date("Date", date_labels = "%b", date_breaks = "1 month", expand = c(0,0)) + 
  scale_y_continuous(expand = c(0,0)) +
  theme_tufte(base_family = "sans")

# Year by year, profit per sale
combined_df %>% 
  group_by(year) %>% 
  mutate(profitpersale_yearlyave = mean(profitpersale_30day),
         date = as.Date(paste("2012", month(date), mday(date), sep = "-"))) %>% 
  ggplot() + 
  geom_line(aes(x=date, y=profitpersale_30day, color = year, group = year)) + 
  geom_hline(aes(yintercept = profitpersale_yearlyave, color = year), alpha = 0.3) +
  scale_x_date("Date", date_labels = "%b", date_breaks = "1 month", expand = c(0,0)) + 
  scale_y_continuous(labels = scales::dollar, expand = c(0,0)) +
  coord_cartesian(ylim = c(0, max(combined_df$profitpersale_30day)))  +
  theme_tufte(base_family = "sans")

# Year by year, profit per order
combined_df %>% 
  group_by(year) %>% 
  mutate(profitperorder_yearlyave = mean(profitperorder_30day),
         date = as.Date(paste("2012", month(date), mday(date), sep = "-"))) %>% 
  ggplot() + 
  geom_line(aes(x=date, y=profitperorder_30day, color = year, group = year)) + 
  geom_hline(aes(yintercept = profitperorder_yearlyave, color = year), alpha = 0.3) +
  scale_x_date("Date", date_labels = "%b", date_breaks = "1 month", expand = c(0,0)) + 
  scale_y_continuous(labels = scales::dollar, expand = c(0,0)) +
  coord_cartesian(ylim = c(0, max(combined_df$profitperorder_30day)))  +
  theme_tufte(base_family = "sans")


# Year by year, revenue per order
combined_df %>% 
  group_by(year) %>% 
  mutate(revenueperorder_yearlyave = mean(revenueperorder_30day),
         date = as.Date(paste("2012", month(date), mday(date), sep = "-"))) %>% 
  ggplot() + 
  geom_line(aes(x=date, y=revenueperorder_30day, color = year, group = year)) + 
  geom_hline(aes(yintercept = revenueperorder_yearlyave, color = year), alpha = 0.3) +
  scale_x_date("Date", date_labels = "%b", date_breaks = "1 month", expand = c(0,0)) + 
  scale_y_continuous(labels = scales::dollar, expand = c(0,0)) +
  coord_cartesian(ylim = c(0, max(combined_df$revenueperorder_30day)))  +
  theme_tufte(base_family = "sans")



# Year by year, monthly revenue
combined_df %>% 
  group_by(year) %>% 
  mutate(profit_yearlyave = mean(profit_30day),
         date = as.Date(paste("2012", month(date), mday(date), sep = "-"))) %>% 
  ggplot() + 
  geom_line(aes(x=date, y=profit_30day, color = year, group = year)) + 
  geom_hline(aes(yintercept = profit_yearlyave, color = year), alpha = 0.3) +
  scale_x_date("Date", date_labels = "%b", date_breaks = "1 month", expand = c(0,0)) +
  scale_y_continuous(labels = scales::dollar, breaks = seq(0, 100000, 500), expand = c(0,0)) +
  theme_tufte(base_family = "sans") 

# Year by year, monthly expenses
combined_df %>% 
  group_by(year) %>% 
  mutate(expenses_yearlyave = mean(expenses_30day),
         date = as.Date(paste("2012", month(date), mday(date), sep = "-"))) %>% 
  ggplot() + 
  geom_line(aes(x=date, y=expenses_30day, color = year, group = year)) + 
  geom_hline(aes(yintercept = expenses_yearlyave, color = year), alpha = 0.3) +
  scale_x_date("Date", date_labels = "%b", date_breaks = "1 month", expand = c(0,0)) +
  scale_y_continuous(labels = scales::dollar, breaks = seq(0, 100000, 500), expand = c(0,0)) +
  theme_tufte(base_family = "sans") 

# Year by year, monthly profit
combined_df %>% 
  group_by(year) %>% 
  mutate(profit_yearlyave = mean(profit_30day),
         date = as.Date(paste("2012", month(date), mday(date), sep = "-"))) %>% 
  ggplot() + 
  geom_line(aes(x=date, y=profit_30day, color = year, group = year)) + 
  geom_hline(aes(yintercept = profit_yearlyave, color = year), alpha = 0.3) +
  scale_x_date("Date", date_labels = "%b", date_breaks = "1 month", expand = c(0,0)) +
  scale_y_continuous(labels = scales::dollar, breaks = seq(0, 100000, 500), expand = c(0,0)) +
  theme_tufte(base_family = "sans") 




# Year by year, annual turnover
combined_df %>% 
  group_by(year) %>% 
  mutate(revenue_yearlyave = mean(revenue_1year),
         date = as.Date(paste("2012", month(date), mday(date), sep = "-"))) %>% 
  ggplot() + 
  geom_line(aes(x=date, y=revenue_1year, color = year, group = year)) + 
  geom_hline(aes(yintercept = revenue_yearlyave, color = year), alpha = 0.3) +
  scale_x_date("Date", date_labels = "%b", date_breaks = "1 month", expand = c(0,0)) +
  scale_y_continuous(labels = scales::dollar, breaks = seq(0, 100000, 5000), expand = c(0,0)) +
  theme_tufte(base_family = "sans") 

# Year by year, annual profit
combined_df %>% 
  group_by(year) %>% 
  mutate(profit_yearlyave = mean(profit_1year),
         date = as.Date(paste("2012", month(date), mday(date), sep = "-"))) %>% 
  ggplot() + 
  geom_line(aes(x=date, y=profit_1year, color = year, group = year)) + 
  geom_hline(aes(yintercept = profit_yearlyave, color = year), alpha = 0.3) +
  scale_x_date("Date", date_labels = "%b", date_breaks = "1 month", expand = c(0,0)) +
  scale_y_continuous(labels = scales::dollar, breaks = seq(0, 100000, 2000), expand = c(0,0)) +
  theme_tufte(base_family = "sans") 

# Year by year, annual expenses
combined_df %>% 
  group_by(year) %>% 
  mutate(expenses_yearlyave = mean(expenses_1year),
         date = as.Date(paste("2012", month(date), mday(date), sep = "-"))) %>% 
  ggplot() + 
  geom_line(aes(x=date, y=expenses_1year, color = year, group = year)) + 
  geom_hline(aes(yintercept = expenses_yearlyave, color = year), alpha = 0.3) +
  scale_x_date("Date", date_labels = "%b", date_breaks = "1 month", expand = c(0,0)) +
  scale_y_continuous(labels = scales::dollar, breaks = seq(0, 100000, 2000), expand = c(0,0)) +
  theme_tufte(base_family = "sans") 


>>>>>>> Stashed changes



# Profit by day of week
combined_df %>% 
<<<<<<< Updated upstream
  group_by(day) %>% 
  summarise(profit = quantile(profit, 0.75)) %>% 
  ggplot() + geom_bar(aes(x = day, y = profit), stat = "identity") + theme_minimal() +
  scale_y_continuous(labels = scales::dollar, breaks = seq(0, 100, 10))  

# Sales by day of week
combined_df %>% 
  group_by(day) %>% 
  summarise(sales = quantile(sales, 0.75)) %>% 
  ggplot() + geom_bar(aes(x = day, y = sales), stat = "identity") + theme_minimal() 
=======
  group_by(year, day) %>% 
  summarise(profit = quantile(profit, 0.75)) %>% 
  ggplot() + geom_bar(aes(x = day, y = profit), stat = "identity") +
  scale_y_continuous(labels = scales::dollar, breaks = seq(0, 100, 10)) +
  facet_wrap("year", ncol = 1) + 
  theme_tufte(base_family = "sans")

# Sales by day of week
combined_df %>% 
  group_by(year, day) %>% 
  summarise(sales = quantile(sales, 0.75)) %>% 
  ggplot() + geom_bar(aes(x = day, y = sales), stat = "identity") + 
  facet_wrap("year", ncol = 1) + 
  theme_tufte(base_family = "sans")
>>>>>>> Stashed changes



# Cost breakdown
cost_df = combined_df %>% 
  mutate(GST = `GST credit` + GST, 
         listing = listing + `private listing` + `multi-quantity`, 
         transaction = transaction + `transaction credit`,
         `auto-renew sold` = `auto-renew sold` + `renew sold` ) %>% 
  select(date, `auto-renew sold`:GST, listing, `Promoted Listings`:`renew expired`,  transaction, printful_cost) %>% 
  gather(cost, value, -date) %>% 
  mutate(value = ifelse(is.na(value), 0, value), 
<<<<<<< Updated upstream
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
=======
         cost = factor(cost, levels = rev(c("renew expired", 
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
  mutate(value_30day = rollapplyr(value, 30, sum, na.rm = TRUE, partial=TRUE))

# Cost stacked
ggplot(data = cost_df, aes(x = date, y = value_30day)) +
  geom_area(aes(colour = cost, fill= cost), position = 'stack') +
  scale_fill_brewer(palette = "Paired") +
  scale_color_brewer(palette = "Paired") + 
  scale_y_continuous(labels = scales::dollar, breaks = seq(0, 10000, 500), expand = c(0,0)) +
  scale_x_date("Date", date_labels = "%b\n%y", date_breaks = "1 month", expand = c(0,0)) + 
  theme_tufte(base_family = "sans")

# Cost percent
ggplot(data = cost_df, aes(x = date, y = value_30day)) +
  geom_area(aes(colour = cost, fill= cost), position = 'fill') +
  scale_fill_brewer(palette = "Paired") +
  scale_color_brewer(palette = "Paired") + 
  scale_x_date("Date", date_labels = "%b\n%y", date_breaks = "1 month", expand = c(0,0)) +
  scale_y_continuous(expand = c(0,0)) + 
  theme_tufte(base_family = "sans")

# Cost stacked excluding Printful
cost_df %>% 
  filter(cost != "printful_cost") %>%
ggplot(aes(x = date, y = value_30day)) +
  geom_area(aes(colour = cost, fill= cost), position = 'stack') +
  scale_fill_brewer(palette = "Paired") +
  scale_color_brewer(palette = "Paired") + 
  scale_y_continuous(labels = scales::dollar, breaks = seq(0, 10000, 500), expand = c(0,0)) +
  scale_x_date("Date", date_labels = "%b\n%y", date_breaks = "1 month", expand = c(0,0)) + 
  theme_tufte(base_family = "sans")

# Cost percent excluding Printful
cost_df %>% 
  filter(cost != "printful_cost") %>% 
ggplot(aes(x = date, y = value_30day)) +
  geom_area(aes(colour = cost, fill= cost), position = 'fill') +
  scale_fill_brewer(palette = "Paired") +
  scale_color_brewer(palette = "Paired") + 
  scale_x_date("Date", date_labels = "%b\n%y", date_breaks = "1 month", expand = c(0,0)) +
  scale_y_continuous(expand = c(0,0)) + 
  theme_tufte(base_family = "sans")

# Recent values
recent_expenses = cost_df %>% 
  select(-value_30day) %>% 
  spread(cost, value) %>% 
  arrange(date) %>% 
  mutate(total = rowSums(.[2:10])) %>% 
  tail(n=10)  





################
# Web scraping #
################

scrape_sales = function(url, element) {
  
  out = ""
  
  while (length(out) < 2) {
    
    #Reading the HTML code from the website
    out = read_html(url) %>% 
          html_nodes(element) %>% 
          html_text() 
  }
  
  return(out)
  
}

# Sale counts

c("https://www.etsy.com/au/shop/InkistPrints",
  "https://www.etsy.com/au/shop/blursbyaiShop",
  "https://www.etsy.com/au/shop/CartoCreative",
  "https://www.etsy.com/au/shop/ScandinavianWalls",
  "https://www.etsy.com/au/shop/iLikeMaps",
  "https://www.etsy.com/au/shop/RobertsMaps",
  "https://www.etsy.com/au/shop/GalaDigitalPrints",
  "https://www.etsy.com/au/shop/TheMapCollection",
  "https://www.etsy.com/au/shop/serenitywallart",
  "https://www.etsy.com/au/shop/EncoreDesignStudios",
  "https://www.etsy.com/au/shop/SaltAndPrinter",
  "https://www.etsy.com/au/shop/ArchTravel",
  "https://www.etsy.com/au/shop/EarthArtAustralia",
  "https://www.etsy.com/au/shop/KRMaps",
  "https://www.etsy.com/au/shop/GrasshopperGeography",
  "https://www.etsy.com/au/shop/PosterArtPrints",
  "https://www.etsy.com/au/shop/LionartPrints",
  "https://www.etsy.com/au/shop/ArtPosterShop",
  "https://www.etsy.com/au/shop/PositiveChangeArt",
  "https://www.etsy.com/au/shop/PrintsHomeDecor",
  "https://www.etsy.com/au/shop/ModernDigitalPrints",
  "https://www.etsy.com/au/shop/MaperyPrints") %>% 
  
  # For each Etsy page, scrape top of page
  map(scrape_sales, ".text-gray-lighter") %>%
  
  # Sales data is in line 103 or line 111
  map_chr(111)  %>% 
  
  # use regex to extract the word immediately before "Sales" and return vector
  map_chr(str_extract, "\\w+(?=\\s+Sales)") %>% 
  
  # Write output to clipboard
  writeClipboard()


# "https://www.etsy.com/shop/iLikeMaps/sold?ref=pagination&page="
# "https://www.etsy.com/shop/TheMapCollection/sold?ref=pagination&page="

all_df = paste0("https://www.etsy.com/shop/MaperyPrints/sold?ref=pagination&page=", 1:25) %>% 
  
  # For each page, scrape all listing names and flatten into character vector
  map(scrape_sales, ".selected-color") %>% 
  flatten_chr() %>% 
  
  # Remove line breaks and hyphens
  gsub(paste(c("\n", "-"), collapse = '|'), '', .) %>% 
  
  # Remove all white space at start and end of string
  trimws(., which = c("both")) %>% 
  
  # Select the first two words, and remove "map" if that is second word
  word(string = ., start = 1, end = 2, sep = " ") %>% 
  gsub(" Map Print", '', .) %>% 
  gsub(" Map", '', .) %>%
  
  # Covert to dataframe and count each unique item
  data_frame(sale = .) %>% 
  count(sale, sort = TRUE)

write_csv(all_df, "maperyprints_data.csv")





library(tidytext)

test_names = c("bird", "animal", "cockatoo", "parrot", "wren", "native animal")


out = expand.grid(name = test_names, page = c(1, 2, 5, 6)) %>% 
  
  # For each name and page, scrape listing titles and expand/unest into rows
  group_by(name, page) %>% 
  mutate(url = paste0("https://www.etsy.com/search?q=", gsub(pattern = " ", "+", name), "&explicit=1&page=", page),
         title = list(scrape_sales(url, ".text-body")[94:189])) %>% 
  unnest(title) %>% 
  
  # Remove duplicates
  distinct(name, page, title) %>% 
  
  # Replace specific place names with 'XX' placeholder, and identify unique bigrams
  mutate(title = gsub(paste(test_names, collapse = '|'), 'XX', title, ignore.case=TRUE)) %>% 
  unnest_tokens(word, title, token = "ngrams", n = 3) %>% 
  ungroup() %>% 
  
  # Count unique works for both low and high ranked pages
  mutate(page_rank = ifelse(page < 4, "high", "low")) %>% 
  count(page_rank, word, sort = TRUE) %>% 
  
  # Spread low and high ranked word counts into two columns
  spread(key = page_rank, value = n, fill = 0) %>% 
  
  # Calculate differences, sort and remove rare categories
  mutate(difference = high - low,
         difference_abs = abs(difference)) %>%
  arrange(-difference) 
 


out %>% 
  group_by(direction = ifelse(difference > 0, 'More high', "More low")) %>%
  top_n(20, difference_abs) %>%
  ungroup() %>%
  mutate(word = reorder(word, difference)) %>%
  ggplot() +
  geom_col(aes(word, difference, fill = direction)) +
  coord_flip() +
  labs(x = "",
       y = 'Difference in number of appearances',
       fill = "",
       title = "High ranked pages vs low ranked pages") +
  scale_y_continuous() +
  guides(fill = guide_legend(reverse = TRUE)) +
  expand_limits(y = c(-4, 4))
  
datapasta::vector_paste()




# Inspecting titles
word_df1 = paste0("https://www.etsy.com/search?q=", test_names, "+map&explicit=1&page=1") %>% 
  
  # For each page, scrape all listing names and flatten into character vector
  map(scrape_sales, ".text-body") %>% 
  flatten_chr() %>% 
  
  # Remove line breaks and hyphens
  gsub(paste(c("\n", "-"), collapse = '|'), '', .) %>% 
  
  # Remove all white space at start and end of string
  trimws(., which = c("both")) %>% 
  
  # Ignore input names
  gsub(paste(test_names, collapse = '|'), 'XX', ., ignore.case=TRUE) %>% 
  
  # Find phrases after converting to dataframe
  data_frame(sale = .) %>% 
  unnest_tokens(word, sale, token = "ngrams", n = 2) %>% 
  count(word, sort = TRUE)

# Inspecting titles
word_df2 = paste0("https://www.etsy.com/search?q=", test_names, "+map&explicit=1&page=10") %>% 
  
  # For each page, scrape all listing names and flatten into character vector
  map(scrape_sales, ".text-body") %>% 
  flatten_chr() %>% 
  
  # Remove line breaks and hyphens
  gsub(paste(c("\n", "-"), collapse = '|'), '', .) %>% 
  
  # Remove all white space at start and end of string
  trimws(., which = c("both")) %>% 
  
  # Ignore input names
  gsub(paste(test_names, collapse = '|'), 'XX', ., ignore.case=TRUE) %>% 
  
  # Find phrases after converting to dataframe
  data_frame(sale = .) %>% 
  unnest_tokens(word, sale, token = "ngrams", n = 2) %>% 
  count(word, sort = TRUE)


word_df1 %>% 
  left_join(word_df2, "word") %>% 
  mutate(difference = n.x - n.y) %>% 
  arrange(-difference) %>% 
  filter(n.x > 50 | n.y > 50) %>% 
  ggplot() + geom_bar(aes(x = word, y = difference), stat = "identity")



# Getting mapzen



setwd("D:/Mapzen")


test = "https://mapzen.com/data/metro-extracts/" %>% 
  read_html() %>% 
  html_nodes(".city") %>% 
  html_attr('href') %>% 
  str_replace("/data/metro-extracts/metro/", "https://s3.amazonaws.com/metro-extracts.mapzen.com/") %>% 
  gsub('.{1}$', ".imposm-shapefiles.zip", .) 



errors = list()

for (i in 47:length(test)) {
  
  url = test[i]
  filename = basename(url)
  
  
  out = tryCatch({
    
    download.file(url, destfile = filename)
    "PASS"
    
  },
  
  error=function(cond) {
    message(paste("URL does not seem to exist:", url))
    message("Here's the original error message:")
    message(cond)
    
    # Choose a return value in case of error
    return("FAIL")
  })
  
  errors[filename] = out
  
}





>>>>>>> Stashed changes


