// Scripts/generateNextSubTopicID.js
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
  const parts = currentID.split('.');

  if (parts.length > 0) {
    const lastPartIndex = parts.length - 1;
    const lastPart = parseInt(parts[lastPartIndex], 10);
    if (isNaN(lastPart)) {
        new Notice("错误：ID的最后一部分不是有效的数字。");
        return "Error_LastPartNotNumber";
    }
    parts[lastPartIndex] = (lastPart + 1).toString();
    return parts.join('.');
  } else {
    new Notice("错误：无法从当前ID解析: " + currentID);
    return "Error_CannotParseID";
  }
} catch (e) {
  new Notice("脚本错误 (SubTopicID): " + e.message);
  return "Error_ScriptFailed";
}