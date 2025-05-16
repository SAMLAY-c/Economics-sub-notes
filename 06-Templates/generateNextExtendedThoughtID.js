// Scripts/generateNextExtendedThoughtID.js
try {
  const activeFile = app.workspace.getActiveFile();
  if (!activeFile) {
    new Notice("错误：没有活动的笔记文件。");
    return "Error_NoActiveFile";
  }
  const currentTitle = activeFile.basename;
  const idMatch = currentTitle.match(/^(\d+(\.\d+)*)/);

  if (!idMatch) {
    new Notice("错误：当前笔记标题没有有效的ID前缀。");
    return "Error_NoIDInCurrentTitle";
  }

  const currentID = idMatch[1];
  // 直接在当前ID后追加 ".1"
  return currentID + ".1";

} catch (e) {
  new Notice("脚本错误 (ExtendedThoughtID): " + e.message);
  return "Error_ScriptFailed";
}