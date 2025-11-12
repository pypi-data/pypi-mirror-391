# Mistral OCR GUI Processor

[![PyPI Version](https://img.shields.io/pypi/v/mistral-ocr-gui)](https://pypi.org/project/mistral-ocr-gui/)

A user-friendly desktop application, built with Python and Tkinter, to perform Optical Character Recognition (OCR) on images using the powerful Mistral AI API. The tool provides a simple interface to process individual images, entire folders, or nested subfolders, and can combine the extracted text into organized markdown files.

## Features

-   **Intuitive Graphical User Interface**: A clean, tabbed interface for different processing modes.
-   **Multiple Processing Modes**:
    -   **Individual Images**: Process one or more specific image files.
    -   **Folder Processing**: Process all supported images within a single folder.
    -   **Subfolder Processing**: Process all supported images within the immediate subdirectories of a parent folder.
-   **Drag-and-Drop Support**: Easily add files or folders by dragging them onto the application window.
-   **Markdown Combination**: Automatically combine OCR results from multiple images into a single, well-structured markdown file.
-   **Flexible Sorting Options**: When combining files, sort them by natural filename order or by modification date.
-   **Real-time Progress Visualization**: A grid of squares visually represents the status of each image (Processing, Completed, Error).
-   **Cancellable Operations**: Stop a long-running processing job at any time.
-   **Concurrent Processing**: Uses a thread pool to process multiple images in parallel, speeding up large jobs.

## Requirements

-   Python 3.8 or higher.
-   A Mistral AI account and an API key. You can get one from the [Mistral AI Platform](https://console.mistral.ai/).

## Installation

The recommended way to install the application is using pip:

```bash
pip install mistral-ocr-gui
```

This command will download the application and automatically install all required dependencies.

### Installation from Source

If you want to contribute to the project or install the latest development version, you can install it from the source code:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Danielnara24/Mistral-OCR.git
    cd Mistral-OCR
    ```

2.  **Install in editable mode:**
    This command will install the application and its dependencies. The `-e` flag allows you to make changes to the source code and have them take effect immediately.
    ```bash
    pip install -e .
    ```

## Configuration: Setting the API Key

The application requires your Mistral API key to be set as an environment variable named `MISTRAL_API_KEY`.

#### Windows

Open Command Prompt or PowerShell and run the following command to set the variable permanently. **You will need to restart your terminal for the change to take effect.**

```powershell
setx MISTRAL_API_KEY "your_api_key_here"
```

#### macOS / Linux

Add the following line to your shell's configuration file (e.g., `~/.bashrc`, `~/.zshrc`, or `~/.profile`):

```bash
export MISTRAL_API_KEY="your_api_key_here"
```

Then, either restart your terminal or run `source ~/.bashrc` (or the relevant file) to apply the changes.

#### Verify the Setup
You can verify that the environment variable is set correctly by running:
-   (macOS/Linux): `echo $MISTRAL_API_KEY`
-   (Windows CMD): `echo %MISTRAL_API_KEY%`
-   (Windows PowerShell): `echo $env:MISTRAL_API_KEY`

## Usage

Once installed, the application can be launched directly from your terminal. Simply run the following command:

```bash
mistral-ocr
```

The graphical user interface will appear, and you can start processing your images.

### How It Works

1.  **Select a Tab**:
    -   **Individual Images**: Use this for processing a specific set of image files from different locations. Each image will generate a corresponding `_OCR.md` file in its original directory.
    -   **Folder**: Use this to process all images inside a single folder. You have the option to combine all the results into one markdown file named `Combined_OCR_[FolderName].md`.
    -   **Subfolders**: Use this to process images located in the immediate subfolders of a parent directory. You can combine results for each subfolder individually and even create a final compilation of all subfolder results.

2.  **Add Files/Folders**:
    -   Click the "Select..." button to open a file/folder dialog.
    -   Or, drag and drop your files/folders directly onto the application window.

3.  **Configure Settings (if applicable)**:
    -   For Folder and Subfolder modes, check the box to enable combining markdown files.
    -   Choose a sorting method for the combined document.

4.  **Process**:
    -   Click the "Process" button to start the OCR job.
    -   The progress grid will update in real-time, showing the status of each file.
    -   A timer will show the elapsed time.

5.  **Output**:
    -   The generated markdown files (`.md`) will be saved in the same directory as the source images or in the relevant parent/subfolder directory for combined files.

## License

This project is licensed under the MIT License.