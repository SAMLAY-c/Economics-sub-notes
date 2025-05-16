<%*
// --- Script Start ---

// 1. Script Initialization and Environment Check
const notice = (msg) => new Notice(msg, 5000);
const log = (msg) => console.log(msg);

const currentFile = app.workspace.getActiveFile();
if (!currentFile) {
    notice("请先打开或保存一个笔记，以确定新文件的存放位置。");
    return;
}

const parentFolder = currentFile.parent;
const currentFileBaseName = currentFile.basename;
const currentFileName = currentFile.name;

// Helper function for path joining, especially handling root
function joinPath(base, ...parts) {
    let path = base;
    if (path === '/') { path = ''; } // Handle root case explicitly
    for (const part of parts) {
        if (part === null || part === undefined || part === "") continue; // Skip empty parts
        if (path === '' || path.endsWith('/')) { 
            path += part.startsWith('/') ? part.substring(1) : part; 
        } else { 
            path += '/' + (part.startsWith('/') ? part.substring(1) : part); 
        }
    }
    path = path.replace(/(?<!:)\/\//g, '/'); // Replace double slashes, but not for protocols like http://
    if (base === '/' && !path.startsWith('/') && path !== '') { path = '/' + path; }
    return path;
}

// 2. Parse Current Filename, Determine Current Main Number (currentMainNumber)
let currentMainNumber;
const fileNamePattern = /^(\d+)\.(\d+)/; // Expects X.Y at the beginning
const matchResult = currentFileName.match(fileNamePattern);

if (matchResult) {
    currentMainNumber = parseInt(matchResult[1], 10);
    log(`Current file has X.Y prefix. Main number (X): ${currentMainNumber}`);
} else {
    log(`Current file "${currentFileName}" does not have X.Y prefix.`);
    let validInitialInput = false;
    while (!validInitialInput) {
        const userInputInitialNumber = await tp.system.prompt(`当前文件名 "${currentFileName}" 没有 'X.Y' 格式的数字前缀。\n请输入一个初始编号 (格式如 '1.0', '0.1') 来重命名当前文件：`, "");
        if (userInputInitialNumber === null || userInputInitialNumber === undefined) { // User cancelled
            log("User cancelled initial number input."); return;
        }
        const initialNumberPattern = /^(\d+)\.(\d+)$/; // Expects X.Y
        const initialMatchResult = userInputInitialNumber.match(initialNumberPattern);
        if (initialMatchResult) {
            currentMainNumber = parseInt(initialMatchResult[1], 10);
            log(`User provided initial number: ${userInputInitialNumber}. Main number (X): ${currentMainNumber}`);
            // Remove existing number prefix from currentFileBaseName if any, to avoid "1.0 1.0 My note"
            const baseNameWithoutOldPrefix = currentFileBaseName.replace(/^(\d+)\.(\d+)\s*/, "");
            let renameBase = `${userInputInitialNumber} ${baseNameWithoutOldPrefix}`;
            let newNameForCurrentFile = renameBase.trim() + ".md"; // Trim in case baseNameWithoutOldPrefix was empty
            let newPathForCurrentFile = joinPath(currentFile.parent.path, newNameForCurrentFile);
            
            let renameCounter = 0;
            const originalRenameBase = renameBase.trim();
            while (await app.vault.adapter.exists(newPathForCurrentFile) && newPathForCurrentFile !== currentFile.path) {
                renameCounter++;
                newNameForCurrentFile = `${originalRenameBase}-${renameCounter}.md`;
                newPathForCurrentFile = joinPath(currentFile.parent.path, newNameForCurrentFile);
            }
            try {
                await app.fileManager.renameFile(currentFile, newPathForCurrentFile);
                notice(`当前文件已重命名为: ${newNameForCurrentFile}`);
                validInitialInput = true;
            } catch (e) {
                notice(`重命名当前文件失败: ${e.message}`); log(`Error renaming file: ${e}`); return;
            }
        } else {
            notice("输入的编号格式不正确，请使用 'X.Y' 格式 (例如 '1.0')。");
        }
    }
}

// 3. Calculate New File's Base Number String
const newMainFileNumber = currentMainNumber + 1;
const newBaseNumberString = `${newMainFileNumber}.1`; // Always X.1 for the next main topic
log(`New base number string for next file: ${newBaseNumberString}`);

// 4. Get User Input for the Rest of the New Filename
const userInputFileNamePart = await tp.system.prompt(`新文件编号: ${newBaseNumberString}. 请输入文件名其余部分:`, "");
if (userInputFileNamePart === null || userInputFileNamePart === undefined || userInputFileNamePart.trim() === "") {
    log("User cancelled or provided empty filename part.");
    notice("操作已取消：未输入文件名。");
    return;
}
// Clean user input: remove .md extension if present and trim whitespace
const cleanedUserInputPart = userInputFileNamePart.trim().replace(/\.md$/i, "");
log(`Cleaned user input part: ${cleanedUserInputPart}`);

// SECTION 4.1 (Category selection) HAS BEEN REMOVED

// 5. Build and Check New Filename for Conflicts
let targetNewFileNameWithoutExt = `${newBaseNumberString} ${cleanedUserInputPart}`;
let newFileCounter = 0;
let finalNewFileName = targetNewFileNameWithoutExt + ".md";
let finalNewFilePath = joinPath(parentFolder.path, finalNewFileName); // Use parentFolder of the *original* currentFile
const originalTargetBaseForNewFile = targetNewFileNameWithoutExt;

log(`Initial target for new file: ${finalNewFilePath}`);
while (await app.vault.adapter.exists(finalNewFilePath)) {
    newFileCounter++;
    finalNewFileName = `${originalTargetBaseForNewFile}-${newFileCounter}.md`;
    finalNewFilePath = joinPath(parentFolder.path, finalNewFileName);
    log(`Conflict found. Trying new name: ${finalNewFilePath}`);
}
log(`Final non-conflicting path for new file: ${finalNewFilePath}`);

// 6. Create and Open the New File using content from "原子笔记.md" and add/update category
try {
    const templateFilePath = "06-Templates/原子笔记.md"; // 请再次确认此路径!
    let templateContent = "";
    try {
        templateContent = await app.vault.adapter.read(templateFilePath);
        log(`Successfully read template file: ${templateFilePath}`);

        // --- MODIFICATION START: Automatically set category to "思考" ---
        const fixedCategory = "思考";
        log(`Attempting to set category to: ${fixedCategory}`);

        const frontmatterRegex = /^---\s*\n([\s\S]*?)\n---\s*\n/; // Regex to capture content between ---
        const fmMatch = templateContent.match(frontmatterRegex);

        if (fmMatch) {
            let fmContent = fmMatch[1]; // The content part of the frontmatter
            const lines = fmContent.split('\n');
            let categoryExists = false;

            // Try to find and update an existing 'category:' line
            for (let i = 0; i < lines.length; i++) {
                if (lines[i].trim().startsWith("category:")) {
                    lines[i] = `category: ${fixedCategory}`;
                    categoryExists = true;
                    log(`Updated existing category line to: category: ${fixedCategory}`);
                    break;
                }
            }

            // If 'category:' line doesn't exist, add it
            if (!categoryExists) {
                let insertAtIndex = lines.length; // Default to adding at the end of current frontmatter lines

                // Try to find a sensible place to insert (e.g., after 'modified:' or 'tags:')
                const commonPrecedingFields = ["modified:", "created:", "tags:", "aliases:", "title:", "id:"];
                let lastKnownFieldIndex = -1;

                for (let i = lines.length - 1; i >= 0; i--) { // Search backwards for last common field
                    for (const field of commonPrecedingFields) {
                        if (lines[i].trim().startsWith(field)) {
                            lastKnownFieldIndex = i;
                            break;
                        }
                    }
                    if (lastKnownFieldIndex !== -1) break;
                }
                
                if (lastKnownFieldIndex !== -1) {
                    insertAtIndex = lastKnownFieldIndex + 1;
                } else if (lines.length > 0 && lines[0].trim() !== "") { 
                    // If no common fields found, but there are lines, insert after the first line
                    insertAtIndex = 1; 
                } else {
                    // If frontmatter lines are empty or just whitespace, insert at the beginning
                    insertAtIndex = 0; 
                }
                
                // Ensure lines array can be spliced correctly even if empty
                if (lines.length === 1 && lines[0].trim() === '') { // Handles case where fmContent was just whitespace
                    lines[0] = `category: ${fixedCategory}`;
                } else {
                    lines.splice(insertAtIndex, 0, `category: ${fixedCategory}`);
                }
                log(`Added new category line: category: ${fixedCategory}`);
            }
            
            fmContent = lines.join('\n');
            // Replace the old frontmatter content (fmMatch[1]) with the new modified fmContent
            templateContent = templateContent.replace(fmMatch[1], fmContent);
            log(`Frontmatter processed for category.`);

        } else {
            // If no frontmatter block is found in the template, create one with the category
            notice("警告：模板文件 \"${templateFilePath}\" 似乎没有标准的 YAML frontmatter。将尝试创建新的 Frontmatter。");
            log("Warning: Standard YAML frontmatter not found in template. Attempting to create new frontmatter.");
            templateContent = `---
category: ${fixedCategory}
---

${templateContent}`; // Prepend new frontmatter
        }
        // --- MODIFICATION END ---

    } catch (templateError) {
        notice(`读取模板文件 "${templateFilePath}" 失败: ${templateError.message}。将使用空内容。`);
        log(`Error reading template file: ${templateError}`);
        templateContent = `# ${targetNewFileNameWithoutExt}\n\n错误：无法加载模板 "${templateFilePath}"。\n${templateError.message}`; // Fallback content
    }

    const createdFile = await app.vault.create(finalNewFilePath, templateContent);
    log(`Successfully created new file with modified template content: ${createdFile.path}`);
    
    // Open the new file in a new leaf
    let leaf = app.workspace.getLeaf('tab'); // 'tab' typically opens in a new tab
    await leaf.openFile(createdFile);
    notice(`新文件已创建并打开: ${finalNewFileName}`);

} catch (e) {
    notice(`创建新文件失败: ${e.message}`);
    log(`Error creating new file: ${e}`);
}

// --- Script End ---
%>