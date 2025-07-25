import pandas as pd
from review_bot import run_for_urls

LISTING_URL = "https://edrater.com/wp-load.php?security_token=361ec2c9919ef335&export_id=1&action=get_data"

# ========== School Listing Loader ==========
def load_school_list():
    """
    Loads the school listing data from a remote CSV URL into a DataFrame.

    Returns:
        pd.DataFrame: DataFrame containing the full list of school listings.

    Raises:
        SystemExit: If the CSV cannot be loaded due to network or format issues.

    Notes:
        - Automatically prints the number of schools loaded for confirmation.
    """
    try:
        df = pd.read_csv(LISTING_URL)
        print(f"Loaded {len(df)} school listings.")
        return df
    except Exception as e:
        print(f"Failed to load data from URL: {e}")
        exit(1)


# ========== User Selection of URLs ==========
def get_url_selection(df):
    """
    Prompts the user to choose which subset of schools to process from the DataFrame.

    Options:
        - 'all': Processes all listings.
        - 'random': Prompts for a number and selects that many listings at random.
        - 'range': Prompts for a start and end index (1-based), and returns that slice.

    Args:
        df (pd.DataFrame): DataFrame containing the full list of school listings,
                           with a 'Permalink' column.

    Returns:
        list: A list of selected school listing URLs.

    Notes:
        - Input validation ensures only valid numbers and ranges are accepted.
        - Keeps asking until a valid option is provided.
        - Converts user-facing 1-based indices to 0-based for DataFrame slicing.
    """
    while True:
        choice = input("Which schools do you want to process? (all / random / range): ").strip().lower()

        if choice == "all":
            return df["Permalink"].tolist()

        elif choice == "random":
            try:
                n = int(input("How many random schools? "))
                return df.sample(n)["Permalink"].tolist()
            except:
                print("Please enter a valid number.")

        elif choice == "range":
            total = len(df)
            print(f"Please enter a range between 1 and {total} (inclusive).")
            try:
                start = int(input("From: "))
                end = int(input("To: "))

                if 1 <= start <= end <= total:
                    return df.iloc[start-1:end]["Permalink"].tolist()
                else:
                    print("Invalid range. Make sure start ≤ end and both are between 1 and", total)
            except:
                print("Please enter valid number.")

        else:
            print("Invalid option. Please choose 'all', 'random', or 'range'.")


# ========== Entry Point for Review Automation ==========
def main():
    """
    Main driver function for the automated school review bot.

    Workflow:
    - Loads the full school listing dataset from the provided URL.
    - Prompts the user to select which subset of schools to process.
    - Passes the selected list of school URLs to be rated and reviewed.
    """
    df = load_school_list()
    urls = get_url_selection(df)
    run_for_urls(urls)

if __name__ == "__main__":
    main()