# Personal-Budget-Dashboard
This is a personal dashboard project developed in Python using Plotly Dash library! Suggestions are welcome!

## This Dashboard provides insights about Personal Expenses Behaviour (upper part of the dashboard) and also gives some information about Investment Performance (lower section of the dashboard)!

## Overall at Dashboard Features:

### Expenses Behaviour section:

The user can select the review period and the macrocategory they wish to assess using the two dropdowns displayed above. These dropdowns dynamically update the data shown on the two charts below. For each macrocategory, there are specific expense categories, allowing users to understand how their expenses are distributed across each macrocategory.

There is also a button that shows User´s Manual, where the user can write down any kind of reminders regarding on the usability of the application as a whole, for instance.

Additionally, a table at the right-hand side shows information on Income and Outflow for the current month. The Outflow is divided into Credit and Debit expenses. It is also divided into ‘Personal’ and ‘Others’, which will be explained further in the ‘Feeding the data into the dashboard’ section. In the same table, users can check the total current credit outflow (Credit Outflow - Total Current) and future invoices (Credit Outflow - Accrued), making it easier to understand payment types for the reviewing month. Lastly, the ‘Investment’ row indicates how much money was sent to the investment account.

At the table immediately bellow, the user can assess Apparent Balance (money currently available on bank account) and Real Balance (Apparent Balance subtracted of the current month Invoice). 

The third table displayed shows ‘pending financial issues’ as reminders of unresolved tasks such as verifying an entry, waiting for a ‘Pending Income’ or ‘Pending Outflow,’ or keeping track of future installment invoices (Accrued Invoice).

### Investment Performance section:
On the left-hand side, the table displayed shows:

- Investment Contribution Target ('Target')
- Investment Contribution Target Deadline ('Deadline')
- Total Accomplished so far of the Investment Contribution Target ('Contribution')
- Pending Contribution ('Pending')
- Percentage Accomplished of the Investment Contribution Target ('% Done')
- Months to Deadline ('Months left')

In the chart immediately to the right, users can visualize the total accomplished and pending contributions. Additionally, historic and cumulative contributions are shown.

It is important to mention that the Target Contribution, Target Deadline and Text for the User´s Manual inputs are provided within the Python script in the ‘DEFINING DASHBOARD INPUTS’ section.

## Importing Data into the Dashboard
It could be done through two different alternatives. The first is simply loading the data as a csv file using pd.read_csv(path). The CSV file is included in the repository as 'Personal Budget Control - Table View.csv'.
And the second alternative is using a Google Sheets through the Google Cloud Platform API. You can access the Google Sheets template using the following link: https://docs.google.com/spreadsheets/d/12wnR-ZyOC_Pssr-Uj4GLOJNxQyToD9azkv8rjKhx8yc/edit?usp=sharing

Please, be aware to apply the following steps at your own Google Sheets file if you want to test the application in your machine.

The second alternative (Google Sheets) follows a pretty simple step by step process, which is covered bellow:

To import data from a Google Sheets spreadsheet into the Plotly Dash dashboard, follow these steps:

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

By loading the data from one of the two alternatives mentioned, the user would need to have the same template used in the reference app.py. So I´ll also leave the CSV template in the end of this file.

## Feeding the data into the dashboard:
The data feeding mechanism is straightforward. All options for data validation are displayed in the ‘Aux’ tab of the Google Sheets, so users need to change their personal options there.

In the ‘Table View’ tab, users only need to provide inputs for the orange-colored columns. For each entry in the table, choose a date, add a description, macrocategory, and category depending on the chosen macrocategory (Google Sheets doesn’t have a native feature that provides ‘conditional data validation’ like Excel). The condition could be either an Income, Outflow, or Investment entry. Then, add a value corresponding to the entry.

For the ‘Status’ column, users can leave it blank or choose from:

- Pending Income (e.g., You pay for your friend’s dinner but expect to be paid back eventually)
- Pending Outflow (e.g., You need to buy a Christmas gift even though it's August)
- Accrued Invoice (e.g., You buy a shirt in installments using your credit card) - Optional
- Verify (e.g., You have an entry but don’t remember its origin, so you need to verify it)

For each of these options in the ‘Status’ column, you can manually assign the corresponding option followed by ‘- Done’ once it’s resolved. For the ‘Pending Income’ option, once the person pays you back, for instance, you can create a new line on the corresponding date with the same features but mark it as ‘Pending Income - Done’ OR simply delete the entry as it does not impact your personal expenses behavior. 

To be able to view expenses classified as 'Others' in the 'Cashflow Overview Selected Month' table, it is necessary to fill in the corresponding entry in the column of the same name: 'Others'

If you have a shared expense but are still waiting for reimbursement, you still can selected 'Others' in the last column and add the corresponding value in a new line on the corresponding date once you have received the money.

The apparent balance value needs to be provided manually in the final rows of the ‘Table View’ tab for every entry update. Be sure to keep the balance entry date updated!

In the investment performance section of the dashboard, you can see the investment contribution target and target deadline inputs. These inputs are provided directly inside the Python code in the [app.py](http://app.py/) file, in the ‘DEFINING INVESTMENT GOALS’ section of the code.

## Running the app!
If you use VSCode, PyCharm or a similar environment, once the code is executed, a link to a local host will appear in the terminal, allowing you to access the dashboard in your web browser.

As mentioned earlier, various aspects still need improvement (data feeding mechanism, code structure, visualization elements, etc.). If you have any suggestions, feel free to reach out and help improve the application!

