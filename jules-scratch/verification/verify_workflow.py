import time
from playwright.sync_api import sync_playwright, Page, expect

def run_verification(page: Page):
    """
    Automates the verification of the NeuroGrid frontend.
    - Registers and logs in a new user.
    - Creates a simple workflow with two nodes.
    - Saves and executes the workflow.
    - Captures a screenshot of the final state with results.
    """
    page.goto("http://localhost:3000")

    # --- 1. Register and Login ---
    username = f"testuser_{int(time.time())}"
    password = "password123"

    page.get_by_placeholder("Username").fill(username)
    page.get_by_placeholder("Password").fill(password)
    page.get_by_role("button", name="Register").click()

    # Expect the UI to update to the authenticated state. Increased timeout.
    expect(page.get_by_role("heading", name="Add Nodes")).to_be_visible(timeout=20000)
    print("User registered and logged in successfully.")

    # --- 2. Add Nodes ---
    page.get_by_role("button", name="Text Summarizer").click()
    page.get_by_role("button", name="Sentiment Analysis").click()

    # Wait for nodes to be added to the DOM
    expect(page.get_by_text("Text Summarizer")).to_be_visible()
    expect(page.get_by_text("Sentiment Analysis")).to_be_visible()
    print("Nodes added to the workflow.")

    # --- 3. Input Data into Nodes ---
    # The first textarea corresponds to the first node added
    summarizer_input_area = page.locator('textarea').nth(0)
    summarizer_input_area.fill("Artificial intelligence is transforming the world in numerous ways, from healthcare to finance.")

    # The second textarea corresponds to the second node
    sentiment_input_area = page.locator('textarea').nth(1)
    sentiment_input_area.fill("I am thrilled with the progress of this project.")
    print("Node inputs filled.")

    # --- 4. Save Workflow ---
    workflow_name = f"My Test Workflow {int(time.time())}"
    page.get_by_placeholder("New Workflow Name").fill(workflow_name)
    page.get_by_role("button", name="Save Current Workflow").click()

    # Wait for the workflow to appear in the dropdown list
    expect(page.get_by_role("option", name=workflow_name)).to_be_visible(timeout=5000)
    print("Workflow saved successfully.")

    # --- 5. Execute Workflow ---
    page.get_by_role("button", name="Run Selected Workflow").click()

    # --- 6. Verify Results and Take Screenshot ---
    # Wait for both result blocks to appear, increasing timeout to account for model loading.
    expect(page.locator('div:has-text("Workflow Output:")')).to_have_count(2, timeout=120000)
    print("Workflow executed and results are visible.")

    # Give a brief moment for final rendering
    time.sleep(1)

    page.screenshot(path="jules-scratch/verification/verification.png")
    print("Screenshot captured successfully.")


if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            run_verification(page)
        except Exception as e:
            print(f"An error occurred during verification: {e}")
            # Save a screenshot on failure for debugging
            page.screenshot(path="jules-scratch/verification/error.png")
        finally:
            browser.close()