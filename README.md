# Personal-Budget-Dashboard
This is a personal dashboard project developed in Python using Plotly Dash library! Suggestions are welcome!

## This Dashboard provides insights about Personal Expenses Behaviour (upper part of the dashboard) and also gives some information about Investment Performance (lower section of the dashboard)!
This is a personal dashboard project developed in Python using Plotly Dash library! Suggestions are welcome!

## Overall at Dashboard Features:

### Expenses Behaviour section:

The user could choose, in the two dropdowns displayed above, the review period and the macrocategory the user would like to assess. The dropdowns change the data displayed on the two charts bellow. For each macrocategory, there are expense categories, so it is possible to understand, in genereal, how your expenses are distributed along each macrocategory. 

There is also a button that shows User´s Manual, where the user can write down any kind of reminders regarding on the usability of the applicarion as a whole, for instance.

Also, I added a table that shows information on Income and Outflow for current month period. I divided the Outflow into Credit and Debit expense. I also divided the Outflow into ‘Personal’ and ‘Others’, which I´ll explain along this file in the ‘Feeding the data into the dashboard’ section! At the same table, the user can also check what is the total current credit outflow (Credit Outflow - Total Current) and also future invoices (Credit Outflow - Accrued), so it eventually makes things easier when understanding types of payments along current month. At last, ‘Investment’ tells the user how much money was sent to investment account. 

At the table immediately bellow, the user can asses Apparent Balance (money currently available on bank account) and Real Balance (Apparent Balance subtracted of the current month Invoice). 

The third table displayed, shows ‘pending financial issues’ as a reminder to the user that are some pendencies to be resolved such as verifyig an entry, waiting for a ‘Pending Income’ ou ‘Pending Outflow’ or even just to keep track of future installment invoices (Accrued Invoice)

The user can select the review period and the macrocategory they wish to assess using the two dropdowns displayed above. These dropdowns dynamically update the data shown on the two charts below. For each macrocategory, there are specific expense categories, allowing users to understand how their expenses are distributed across each macrocategory.

A button is available to show the User’s Manual, where users can write down any kind of reminders regarding the usability of the application as a whole.

Additionally, a table shows information on Income and Outflow for the current month. The Outflow is divided into Credit and Debit expenses. It is also divided into ‘Personal’ and ‘Others’, which will be explained further in the ‘Feeding the data into the dashboard’ section. In the same table, users can check the total current credit outflow (Credit Outflow - Total Current) and future invoices (Credit Outflow - Accrued), making it easier to understand payment types for the current month. Lastly, the ‘Investment’ row indicates how much money was sent to the investment account.

In the table immediately below, users can assess the Apparent Balance (money currently available in the bank account) and the Real Balance (Apparent Balance minus the current month’s Invoice).

The third table displayed shows ‘pending financial issues’ as reminders of unresolved tasks such as verifying an entry, waiting for a ‘Pending Income’ or ‘Pending Outflow,’ or keeping track of future installment invoices (Accrued Invoice).

### Investment Performance section:
On the left-hand side, six tables are displayed showing:

- Investment Contribution Target ($ Target)
- Investment Contribution Target Deadline (Target Deadline)
- Total Accomplished so far of the Investment Contribution Target ($ Accomplished)
- Pending Contribution ($ Pending)
- Percentage Accomplished of the Investment Contribution Target (% Accomplished)
- Months to Deadline (Months Deadline)

In the chart immediately to the right, users can visualize the total accomplished and pending contributions. Additionally, historic and cumulative contributions are shown.

It is important to mention that the Target Contribution and Target Deadline inputs are provided within the Python script in the ‘DEFINING INVESTMENT INPUT GOALS’ section.

## Importing Data from a Google Sheets Spreadsheet into the Dashboard
It could be done through two different alternatives. The first is simply loading the data as a csv file using pd.read_csv(path) or using a Google Sheets through the Google Cloud Platform API. This second alternative follows a pretty simple step by step process, wich is covered bellow:

To import data from a Google Sheets spreadsheet into a Dash-created dashboard, follow these steps:

1. **Create a project on Google Cloud Platform (GCP) and enable the Google Sheets and Google Drive APIs**:
    - Go to the [Google Cloud Console](https://console.cloud.google.com/).
    - Create a new project.
    - Enable the Google Sheets and Google Drive APIs for the project.
2. **Create service account credentials**:
    - In the Google Cloud Console, navigate to the "Credentials" section and create a new service account.
    - Download the JSON credentials file and save it securely on your system.
3. **Share your Google Sheets spreadsheet with the service account**:
    - Open your Google Sheets spreadsheet.
    - Share the spreadsheet with the service account email (which can be found in the JSON credentials file).
4. **Install the necessary libraries in your development environment**:
    - Install the `gspread` and `oauth2client` libraries using pip:
        
        ```bash
        pip install gspread oauth2client
        
        ```
        
5. **Implement the authentication and data import in your Python code**:
    - Use the following code as a base to authenticate and import data from your Google Sheets spreadsheet:
    
    ```python
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    
    # Define the scope
    scope = ["<https://spreadsheets.google.com/feeds>", "<https://www.googleapis.com/auth/drive>"]
    
    # Service Account Credentials
    credentials = ServiceAccountCredentials.from_json_keyfile_name("PATH_TO_YOUR_JSON_FILE", scope)
    
    # Google Sheets Authentication and Opening
    gc = gspread.authorize(credentials)
    sheet = gc.open('YOUR_SPREADSHEET_NAME').sheet1
    
    # Select Google Sheets Columns for dashboard analysis
    data = sheet.get_all_records(expected_headers=[
        'Date',
        'Month',
        'Year',
        'Description',
        'Macrocategory',
        'Category',
        'Condition',
        'Value',
        'Value Calculation',
        'Status',
        'Type',
        'Shared'
    ])
    
    ```
    

Replace `"PATH_TO_YOUR_JSON_FILE"` with the path to your JSON credentials file and `'YOUR_SPREADSHEET_NAME'` with the name of your spreadsheet.

With these steps, you will be ready to import data from a Google Sheets spreadsheet into your Dash dashboard. Ensure all steps are followed correctly to guarantee the data import works smoothly.

By loading the data from one of the two alternatives mentioned, the user would need to have the same template used in the reference app.py. So I´ll also leave the Google Sheets and CSV templates in the end of this file.

## Feeding the data into the dashboard:
The data feeding mechanism is straightforward. All options for data validation are displayed in the ‘Aux’ tab of the Google Sheets, so users need to change their personal options there.

In the ‘Table View’ tab, users only need to provide inputs for the orange-colored columns. For each entry in the table, choose a date, add a description, macrocategory, and category depending on the chosen macrocategory (Google Sheets doesn’t have a native feature that provides ‘conditional data validation’ like Excel). The condition could be either an Income, Outflow, or Investment entry. Then, add a value corresponding to the entry.

For the ‘Status’ column, users can leave it blank or choose from:

- Pending Income (e.g., You pay for your friend’s dinner but expect to be paid back eventually)
- Pending Outflow (e.g., You need to buy a Christmas gift even though it's February)
- Accrued Invoice (e.g., You buy a shirt in installments using your credit card) - Optional
- Verify (e.g., You have an entry but don’t remember its origin, so you need to verify it eventually)

For each of these options in the ‘Status’ column, you can manually assign ‘- Done’ once it’s resolved. For the ‘Pending Income’ option, once the person pays you back, you can create a new line on the corresponding date with the same features but mark it as ‘Pending Income - Done’ OR simply delete the entry as it does not impact your expenses behavior. If you have a shared expense but are still waiting for reimbursement, you can choose ‘Shared’ in the last column and add the corresponding value in a new line on the corresponding date once you have received the money.

The apparent balance value needs to be provided manually in the final rows of the ‘Table View’ tab for every entry update. Be careful to keep the balance entry date updated!

In the investment performance section of the dashboard, you can see the investment contribution target and target deadline inputs. These inputs are provided directly inside the Python code in the [app.py](http://app.py/) file, in the ‘DEFINING INVESTMENT GOALS’ section of the code.

## Running the app!
If you use VSCode, PyCharm or a similar environment, once the code is executed, a link to a local host will appear in the terminal, allowing you to access the dashboard in your web browser.

As mentioned earlier, various aspects still need improvement (data feeding mechanism, code structure, visualization elements, etc.). If you have any suggestions, feel free to reach out and help improve the application!

