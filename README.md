# mass_rewriter
Extension for WEbUI

This is a comprehensive script for a "Mass Rewriter" extension. Let's break down its functionality item by item.

---

## Mass Rewriter: User Guide

The Mass Rewriter extension for text-generation-webui allows you to process large amounts of text (from plain text files or JSON datasets) by applying rewrite instructions using a Large Language Model (LLM). You can customize templates, manage how text is split, and control various aspects of the generation and output.

---

### 1. Getting Started: Loading Your Data

Before rewriting, you need to load your source text. The extension supports plain text files (.txt) and JSON files (.json).

**Tab: `Text` (for .txt files)**

*   **Input file (`inputfile_text_drop`):**
    *   **How to Use:** Select your `.txt` file from this dropdown. It lists files found in the `extensions/mass_rewritter/inputs/` directory.
    *   Click the refresh button (🔄) next to the dropdown if you've added new files to the `inputs` folder and they don't appear.
*   **Load Blockified text (Sub-tab):**
    *   **Block split (`gr_par_split`):**
        *   **How to Use:** Defines the character sequence that separates individual "blocks" or paragraphs in your plain text file. The default is `\n\n\n` (three newlines).
        *   **Purpose:** This tells the tool how to divide your text file into manageable chunks for the LLM to process one by one.
    *   **Load (`text_btn_load`):**
        *   **Action:** After selecting your file and confirming the `Block split` delimiter, click this button.
        *   **What it Does:** Loads the text file. The `infotext` area below will confirm the number of paragraphs/blocks loaded. The `Output filename` will also be pre-filled based on your input file and the current model name.
*   **Blockify normal text (Sub-tab):** (See Section 2: Preparing Your Input Text)
*   **Extract names (Sub-tab):** (See Section 2: Preparing Your Input Text)

**Tab: `JSON` (for .json files)**

*   **Input file (`inputfile_text_drop_JSON`):**
    *   **How to Use:** Select your `.json` file from this dropdown. It lists files from the `extensions/mass_rewritter/inputs/` directory.
    *   Click the refresh button (🔄) if new files aren't visible.
*   **JSON Type (`gr_JSONType`):** This is crucial for how the JSON data is interpreted and rewritten.
    *   **`Instruction -> LLM -> Instruction, Output -> Output` (Default):**
        *   The content of your JSON's `instruction` field is fed to the LLM.
        *   The LLM's rewritten text replaces the original `instruction` field.
        *   The original `output` field in your JSON remains unchanged.
        *   **Use Case:** Ideal if you want to rewrite or augment the "instructions" or "prompts" in your dataset.
    *   **`Instruction -> Instruction, Output -> LLM -> Output`:**
        *   The content of your JSON's `output` field is fed to the LLM.
        *   The LLM's rewritten text replaces the original `output` field.
        *   The original `instruction` field in your JSON remains unchanged.
        *   **Use Case:** Ideal if you want to rewrite or augment the "responses" or "completions" in your dataset.
*   **Load JSON (`text_btn_load_JSON`):**
    *   **Action:** After selecting the file and the correct `JSON Type`, click this button.
    *   **What it Does:** Loads the JSON data. The `infotext` area will confirm the number of items loaded and how the fields will be used based on your `JSON Type` selection.

---

### 2. Preparing Your Input Text (Optional Tools)

These tools are found under the `Text` tab and help pre-process your plain text files.

**Blockify normal text (Sub-tab under `Text`)**

This tool helps convert a standard text file (e.g., a book chapter) into a "blockified" format, where text is split into chunks suitable for LLM processing.

*   **Block size (in chars) (`gr_block_size`):**
    *   **How to Use:** Enter the maximum desired character length for each block (e.g., `850`).
*   **Chapter word (`gr_par_split_chapter`):**
    *   **How to Use:** If your text uses a consistent word to mark new chapters (e.g., "CHAPTER", "Chapter"), enter it here.
    *   **Purpose:** Helps ensure that chapter headings start new blocks, preventing them from being merged with previous paragraphs.
*   **Convert to Blocks (`gr_convert_to_Block`):**
    *   **Action:** After selecting a file in the main `Input file` dropdown (under `Text` tab) and setting the `Block size` / `Chapter word`, click this.
    *   **What it Does:** Reads the selected `.txt` file, splits it into blocks based on your settings, and saves a *new* `.txt` file in the `extensions/mass_rewritter/inputs/` folder. The new filename will include a suffix like `.blocks850.txt`. You can then load this new blockified file using the "Load Blockified text" tab.

**Extract names (Sub-tab under `Text`)**

*   **Extract Names (`gr_extractNames_button`):**
    *   **Action:** First, load a plain text file using the "Load Blockified text" tab. Then, click this button.
    *   **What it Does:** Scans the entire loaded text for words that are likely to be names (capitalized, appear multiple times, and are not common English words or titles). The extracted names, sorted by frequency, will appear in the `Names that appear more than once...` textbox below the button.
    *   **Use Case:** Helps you identify names in your text that you might want to replace using the "Names" replacement feature (see Section 3).

---

### 3. Configuring the Rewriting Process

This section covers how you instruct the LLM to perform the rewrites.

**Accordion: `Edit Template`**

*   **Template Selector (`para_templates_drop`):**
    *   **How to Use:** Choose from a list of predefined templates stored in `extensions/mass_rewritter/Template/`. `None` or `default` might be initial options.
    *   Click the refresh button (🔄) if you've added new template files manually.
    *   **What it Does:** Loads the selected template's content into the "Main Template" and "Examples" textboxes below.
*   **Tab: `Main Template` (`para_template_text`):**
    *   **How to Use:** This is the core instruction given to the LLM for each block of text.
    *   **Crucial:** You **must** include the placeholder `<|context|>` where the actual text block from your loaded file should be inserted.
    *   You can also use `<|user|>` and `<|bot|>` placeholders, which will be replaced by the prompts defined in the "Model Instruct Prompts" section (see below).
    *   *Example:* `Rewrite the following text in a more formal tone:\n<|user|>Here is the text:\n<|context|>\n<|bot|>Here is the formal version:`
*   **Tab: `Alt Template (for double-gen)` (`para_template_text2`):**
    *   **How to Use:** If you enable "Double-gen" (see Settings below), the LLM processes each block twice. This template is used for the *second* LLM pass. The output of the first pass becomes the `<|context|>` for this template.
    *   If left empty, the "Main Template" will be used for both passes.
*   **Tab: `Examples` (`para_template_exampletext`):**
    *   **How to Use:** Provide a few examples (few-shot learning) to guide the LLM's output style. Format these examples exactly like your "Main Template", including `<|user|>`, `<|bot|>`, and example `<|context|>` with its desired rewritten version. Separate examples with newlines.
    *   **Purpose:** Helps the LLM better understand the desired output format and style.
*   **Tab: `Names` (Name Replacement):**
    *   **Randomly Replace names/places (`names_replace`):**
        *   **How to Use:** Check this box to enable automatic name/place replacement in the input text *before* it's sent to the LLM.
        *   **Important:** This feature is **not compatible** if you have loaded a JSON file and are using one of the "JSON cross modes" (where `JSONType` involves using one JSON field as input and another as static output). It works best with plain text inputs or JSON inputs where only one field is actively processed by the LLM.
    *   **Female Names (`names_she`), Male Names (`names_he`), Last Names (`names_last`), Towns (`names_places1`), Places/Churches (`names_places2`):**
        *   **How to Use:** Enter comma-separated lists of names/places into the respective textboxes. For example, in `Female Names`, you might put: `Alice,Betty,Carol`.
        *   **What it Does:** If `Randomly Replace names/places` is checked, the tool will find occurrences of the names you listed in these boxes within the `<|context|>` text and replace them with a random name from the *internal predefined lists* (e.g., `female_names`, `male_names` hardcoded in the script). The names you enter here are the *targets for replacement*, not the source of replacements.
        *   **Use Case:** Anonymizing data or creating diverse datasets by varying entities.
*   **Save Template:**
    *   **Filename Textbox (`templ_filename`):** Enter a name for your new or modified template (e.g., `my_rewrite_style`). Do not add `.txt`.
    *   **Save Template (`templ_btn_save`):** Click to save the current content of "Main Template" and "Examples" textboxes.
    *   **What it Does:** Saves `your_filename.txt` (for Main Template) and `your_filename_examples.txt` (for Examples) into the `extensions/mass_rewritter/Template/` directory. The filename textbox will show `<Saved>` on success. The "Template Selector" dropdown will update.

**Accordion: `Settings` (nested within "Edit Template")**

These settings control the generation process:

*   **Generate Output: Text \[in]-> (LLM) -> LLM Text \[out] (`gr_generate`):**
    *   **How to Use:** Check this to actually use the LLM for rewriting.
    *   If unchecked, the input text (`<|context|>`) is copied directly to the output. Useful for testing other settings or data flow without LLM calls.
*   **Double-gen: Text \[in]-> (LLM) -> (LLM) -> LLM Text \[out] (`gr_generate2`):**
    *   **How to Use:** Check this to process each text block through the LLM twice. The first LLM output becomes the input (`<|context|>`) for the second LLM pass (which uses the "Alt Template" if provided).
*   **REVERSE Training: LLM Text\[out] -> instruction, Text\[in] -> output (`gr_radioReverse`):**
    *   **How to Use:** (Primarily for JSON output) If checked, the LLM's generated output will be saved as the `instruction` field in the output JSON, and the original input text (`<|context|>`) will be saved as the `output` field.
    *   If unchecked (default), the original input text (or its corresponding JSON field key) becomes the `instruction`, and the LLM's output becomes the `output`.
*   **Replace \\n in Text \[in] with space (`gr_rep_EOL`):**
    *   **How to Use:** If checked, all single newline characters (`\n`) within the `<|context|>` text are replaced with a space before sending to the LLM.
*   **Replace \\n\\n with one \\n in Text \[in] (`gr_rep_EOL2`):**
    *   **How to Use:** If checked, sequences like `\n\n` or `\n \n` in the `<|context|>` are condensed to a single `\n`.
*   **Internally Remove \\n before it goes to LLM, but keep it in Text \[in] (`gr_rmove_EOL`):**
    *   **How to Use:** If checked, newlines are temporarily removed from the text sent to the LLM, but the original newlines are preserved in the "Text \[in]" display and in the data saved (e.g., if JSON output saves the original input).
*   **Add grammatical errors (`gr_add_err`):**
    *   **How to Use:** Check this to intentionally introduce grammatical errors into the LLM's output.
*   **Error level (`gr_add_err_level`):**
    *   **How to Use:** Slider (1-10) to control the frequency/intensity of introduced errors if `Add grammatical errors` is checked.
*   **Max new tokens (`gr_max_new_tokens`):**
    *   **How to Use:** Sets the maximum number of tokens the LLM can generate for each rewritten block. This is a primary control from the main WebUI interface reflected here.
*   **if reply is much longer (3x) than IN: Copy IN -> OUT (otherwise ignore) (`gr_rep_Include_Long`):**
    *   **How to Use:** If the LLM's output is more than 3 times longer than the input text, checking this will cause the original input text to be used as the output instead. If unchecked, such long replies are still processed (or potentially skipped based on other rules).
*   **if reply is much shorter (3x) than IN then skip (`gr_rep_skip_short`):**
    *   **How to Use:** If the LLM's output is less than 1/3 the length of the input text, checking this will cause this item to be skipped entirely (not saved to output).
*   **SHORT IN cutoff characters (`gr_small_lines`):**
    *   **How to Use:** Define a character count (e.g., `20`).
*   **if IN is SHORT: Copy IN -> OUT (otherwise ignore) (`gr_rep_Include`):**
    *   **How to Use:** If an input text block is shorter than the `SHORT IN cutoff characters`, checking this will copy the original input directly to the output without LLM processing.
*   **Repeat each block n times (`repeat_times`):**
    *   **How to Use:** Enter a number (e.g., `3`). Each input block will be processed by the LLM this many times, potentially generating different outputs if your model/settings have randomness.
*   **Save Current Settings (`save_btn`):**
    *   **Action:** Click to save all current settings from this accordion (and other persistent params like User/Bot prompts, output type) to `massrewriter.json` in the extension's root directory. These settings will be loaded the next time you open the extension.

**Model Instruct Prompts (Section below `Settings` accordion, above `Text [in]`)**

This section defines the user and assistant/bot markers used in your templates.

*   **Model Instruct (OLD) (`preset_type`):**
    *   **How to Use:** Select a model type (e.g., "Alpaca", "Vicuna", "ChatML").
    *   **What it Does:** Automatically fills the `Replace <|user|> with` and `Replace <|bot|> with` fields with common prompt formats for that model type. Select "Custom" to define them manually.
*   **Replace <|user|> with (`text_USR`):**
    *   **How to Use:** The text here will replace `<|user|>` in your "Main Template" and "Examples".
*   **Replace <|bot|> with (`text_BOT`):**
    *   **How to Use:** The text here will replace `<|bot|>` in your "Main Template" and "Examples".

---

### 4. Output Configuration

This section, below the main input/output text areas, defines how your rewritten data is saved.

*   **Output: JSON or Plain TEXT (`gr_radio`):**
    *   **JSON:** Saves output as a JSON Lines file (`.json`), where each line is a JSON object typically containing "instruction" and "output" fields (or as configured by `REVERSE Training`).
    *   **Plain TEXT:** Saves output as a `.txt` file, where each rewritten block is separated by the delimiter defined in `Plain text paragraph separator`.
*   **JSON instruct (ALT on separate lines) (`text_instruct`):**
    *   **How to Use:** (Only if `Output` is JSON) This text becomes the content of the `instruction` field in your output JSON (unless `REVERSE Training` is used, or if loading from JSON and the instruction field is preserved).
    *   If you provide multiple lines of text here, the script will cycle through them for each entry in the output JSON.
    *   *Example:* If your main template is just `<|context|>`, you could put `Rewrite this:` here.
*   **Output filename (`out_filename`):**
    *   **How to Use:** The base name for your output file (e.g., `my_rewritten_data`). The extension (`.json` or `.txt`) will be added automatically. This is usually pre-filled when you load an input file.
*   **Plain text paragraph separator (`plaintext_instruct`):**
    *   **How to Use:** (Only if `Output` is Plain TEXT) Defines the characters that separate each rewritten block in the output `.txt` file. Default is `\n\n` (two newlines).

---

### 5. Running and Monitoring

*   **Text \[in] (`text_in`):**
    *   Displays the current text block (`<|context|>`) being processed.
    *   **`<<` (`prev_prevbtn`) and `>>` (`prev_nextbtn`):** Use these buttons to manually preview the loaded input blocks *before* starting the main process.
*   **LLM Text \[out] (`text_out`):**
    *   Displays the LLM's generated output for the current "Text \[in]".
*   **Start (`start_btn`):**
    *   **Action:** Click to begin the mass rewriting process based on all your configurations.
    *   **Monitoring:** The area below this button (`infotext2` and a temporary HTML display `gr_htmlDisp`) will show:
        *   Progress (e.g., `Epoch: 1/1 : Progress: X/Y`)
        *   Speed (iterations/second or seconds/iteration)
        *   Elapsed time and estimated time remaining.
*   **Cancel (`cancel_btn`):**
    *   **Action:** Click to stop the ongoing process. The tool will attempt to finish the current item and save any work done so far before stopping.
*   **Infotext Area (`infotext2`):**
    *   Shows status messages like "Ready", "Preparing...", "Starting...", "Interrupted", or "Finished".

---

### 6. Saving Your Results

*   **Automatic Saving:**
    *   During a long run, the tool automatically saves the current output (JSON or TXT) every 10 processed items. This prevents data loss if the process is interrupted.
    *   When starting a JSON output generation, if an `output.json` (or your custom named file) already exists, it will be backed up to `output_backup.json`.
*   **Final Save:**
    *   When the process completes normally or is canceled via the `Cancel` button, the full output file is saved to the extension's root directory (e.g., `extensions/mass_rewritter/output.json` or `extensions/mass_rewritter/your_filename.txt`).
*   **Persistent Settings:**
    *   Clicking "Save Current Settings" in the `Settings` accordion saves your configuration to `massrewriter.json`.

---

### 7. Important Considerations

*   **LLM Choice:** The quality and style of your rewritten text heavily depend on the LLM you have loaded in the main text-generation-webui.
*   **Token Limits:** Be mindful of your LLM's context window. The `Block size` (during blockification) and `Max new tokens` settings are important for managing this.
*   **Experimentation:** Many settings interact. It's often best to test with a small subset of your data first to fine-tune your templates and settings before running on a large dataset.
*   **File Paths:** The extension expects input files in `extensions/mass_rewritter/inputs/` and templates in `extensions/mass_rewritter/Template/`. Output files are saved in `web_ui root folder`.

---
