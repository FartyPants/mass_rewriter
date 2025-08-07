# mass_rewriter
Extension for WebUI 

# Mass Rewriter: User Guide V2

This tool helps you automate the process of modifying text in bulk using an AI model. You can load plain text files or JSON datasets, apply various transformations, and then save the rewritten content.

## There is much more detailed ste[-by-ste[ explanation in my book "The Cranky Man's Guide to LoRA & QLoRA" 

<img width="200" height="320" alt="The Cranky Man's Guide to LoRA & QLoRA" src="https://github.com/user-attachments/assets/afdbaae1-54a6-421f-a52c-ce6ea4477514" />

Find it on [Amazon](https://www.amazon.com/dp/B0FLBTR2FS), [Apple Books](https://books.apple.com/us/book/the-cranky-mans-guide-to-lora-and-qlora/id6749593842), [Kobo](https://www.kobo.com/ca/en/ebook/the-cranky-man-s-guide-to-lora-and-qlora), [Barnes & Noble](https://www.barnesandnoble.com/w/the-cranky-mans-guide-to-lora-and-qlora-f-p-ham/1148001179)

Also :

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/Q5Q5MOB4M)


Version 2.0

---

## 1. Getting Started: Loading Your Data

Before you can rewrite anything, you need to load your source text. You have two main options:

### Load Plain Text File (Tab: 'Text')

*   **Input File (`inputfile_text_drop`):**
    *   **How to Use:** Select your `.txt` file from the "Input file" dropdown. The list automatically populates with `.txt` files found in `extensions/mass_rewritter/inputs/`. Click the refresh button (🔄) if you've added new files.
    *   **Action:** After selecting your file, click the **"Load" button**.
    *   **What it Does:** This loads the text file into memory, splitting it into individual "blocks" based on the "Block split" setting.
*   **Block split (`gr_par_split`):**
    *   **How to Use:** This textbox defines what separates your blocks. `\\n\\n\\n` (three newlines) is the default. You can change this if your file uses a different separator (e.g., `###`).

### Load JSON File (Tab: 'JSON')

*   **Input File (`inputfile_text_drop_JSON`):**
    *   **How to Use:** Select your `.json` file from this dropdown. The list will populate with `.json` files from `extensions/mass_rewritter/inputs/`.
*   **JSON Operation (`gr_JSONType`):**
    *   **How to Use:** This is the most crucial setting for JSON. It tells the tool exactly how to process your data. Select one of the four unambiguous operations.
    *   **Action:** After selecting the file and JSON Operation, click the **"Load JSON" button**.
    *   **What it Does:** Loads the JSON data according to your chosen operation. See the detailed breakdown below.

## 2. Preparing Your Input Text (Optional Tools)

These tools help you organize or analyze your text before rewriting.

*   **Blockify Text (Tab: 'Text' -> 'Blockify text'):**
    *   **What it Does:** Takes a selected plain text file and breaks it down into smaller, consistently sized blocks. It saves a *new* `.txt` file (e.g., `mybook.blocks850.txt`) in the `inputs` folder. This is useful for processing long documents that aren't already separated into paragraphs.
*   **Extract Names (Tab: 'Text' -> 'Extract names'):**
    *   **What it Does:** Scans the selected plain text file and lists frequently occurring proper nouns. This helps you quickly identify names to use with the "Randomly Replace names/places" feature.
*   **Export (Tab: 'Text' -> 'Export'):**
    *   **What it Does:** Takes the currently loaded text blocks and saves them as a simple JSONL file where each line is `{"text": "your text block"}`. This is ideal for preparing data for completion model fine-tuning.

## 3. Configuring the Rewriting Process (Templates & Settings)

This is where you tell the AI *how* to rewrite your text.

### Edit Template (Accordion)

*   **Template Selector (`para_templates_drop`):** Choose a pre-saved prompt template.
*   **Main Template (`para_template_text`):** Your primary instruction to the LLM. **Crucially, include the `<|context|>` placeholder**, which is where the text from your loaded file will be inserted.
*   **Alt Template (for double-gen) (`para_template_text2`):** A secondary prompt used for the second pass if `Double-generation` is enabled. If empty, the Main Template is used for both passes.
*   **Examples (`para_template_exampletext`):** Provide "few-shot" examples to better guide the LLM's output style.
*   **Save Template:** Save your current Main Template and Examples for future use.

### A Short Guide to Crafting Effective Templates

The **Main Template** is the most powerful feature of the Mass Rewriter. It is the blueprint for every single prompt that gets sent to the language model.

#### The Three Magic Placeholders

1.  **`<|context|>` (Mandatory):** This is where the actual text from your source file will be inserted. **Your template must always contain `<|context|>` exactly once.**
2.  **`<|user|>` (Recommended):** This placeholder is replaced by whatever you have in the **User String** field (e.g., `### Human:`, `USER:`). It helps create structured, chat-like prompts.
3.  **`<|bot|>` (Recommended):** This placeholder is replaced by whatever you have in the **Assistant String** field (e.g., `### Assistant:`, `[/INST]`). It signals to the model where its response should begin.

### Settings (Accordion)

*   **Generate with LLM (`gr_generate`):** Uncheck this to test the data flow without using the LLM. The tool will simply copy the source text based on your JSON Operation.
*   **Double-generation (`gr_generate2`):** Processes each item with the LLM twice for more refined results.
*   **For Plain Text: Generate `instruction` from text (`gr_radioReverse`):**
    *   **How to Use:** This checkbox **only affects Plain Text workflows**. When checked, the LLM's goal is to generate the `instruction` field, and the original text is copied to the `output` field.
    *   **Use Case:** Ideal for creating instruction/response pairs from a list of raw texts.
*   **Add grammatical errors (`gr_add_err`):** Intentionally adds grammatical mistakes to the LLM's final output.
*   **Skip if reply is >3x longer than input (`gr_rep_skip_Long`):** If the LLM generates an unusually long response, the entire item is skipped.
*   **Skip if input is shorter than (chars) (`gr_small_lines`):** Prevents the tool from processing very short or empty lines.
*   **Repeat each item N times (`repeat_times`):** Processes each input item multiple times to augment your dataset.
*   **Save All Settings (`save_btn`):** Saves all your current settings to `massrewriter.json`.

### Instruction Format (User/Assistant Strings)

*   **Instruction Format Preset (`preset_type`):** Select a well-known model format (e.g., "Alpaca," "ChatML") to automatically fill the User/Assistant strings below.
*   **User String (`text_USR`) & Assistant String (`text_BOT`):** These fields define what the `<|user|>` and `<|bot|>` placeholders in your template are replaced with.

### Names (Tab: 'Names')

*   **Randomly Replace names/places (`names_replace`):**
    *   **How to Use:** Check to enable name replacement. **Note:** This feature is incompatible with JSON workflows and will be automatically disabled.
    *   **What it Does:** Replaces names you list in the boxes below with random names from the tool's built-in lists.

## 4. Output Configuration

*   **Output Format (`gr_radio`):** Choose to save as a structured `JSON` file or a simple `Plain TEXT` file (containing only LLM outputs).
*   **Prefix for `instruction` field (`text_instruct`):** Adds a prefix to the `instruction` field in the final JSON. If you enter multiple lines, it will cycle through them.
*   **Output filename (`out_filename`):** The base name for your output file (e.g., `my_data_rewritten`).

## 5. Running and Monitoring

*   **Start (`start_btn`):** Begins the bulk processing job.
*   **Cancel (`cancel_btn`):** Safely stops the current job and saves all progress made so far.
*   **Text [in] & LLM Text [out]:** These boxes show the current text being processed by the LLM and its real-time response.
*   **`<<` & `>>` buttons:** Manually browse through the loaded input blocks before starting a job.
*   **Progress Bar & Timers:** The area below the Start/Cancel buttons provides real-time progress, speed (it/s), and estimated time remaining.

## 6. Saving Your Results

*   **Automatic Saving:** Progress is saved automatically every 10 items.
*   **Final Save:** The complete output file is saved when the job finishes or is canceled.
*   **Backup:** When starting a new job, the tool automatically backs up your previous output file (e.g., `output_backup.json`) to prevent accidental data loss.
