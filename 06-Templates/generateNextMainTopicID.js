// Scripts/generateNextMainTopicID.js
try {
  const activeFile = app.workspace.getActiveFile();
  if (!activeFile) {
    new Notice("错误：没有活动的笔记文件。");
    return "Error_NoActiveFile";
  }
  const currentTitle = activeFile.basename; // 获取不带扩展名的文件名
  const idMatch = currentTitle.match(/^(\d+(\.\d+)*)/); // 匹配开头的ID

  if (!idMatch) {
    new Notice("错误：当前笔记标题没有有效的ID前缀。");
    return "Error_NoIDInCurrentTitle";
  }

  const currentID = idMatch[1];
  const parts = currentID.split('.');

  if (parts.length > 0) {
    const newMainPart = (parseInt(parts[0], 10) + 1).toString();
    // 根据您的示例 1.5.1 -> 2.1
    return newMainPart + ".1";
  } else {
    new Notice("错误：无法从当前ID解析出主部分: " + currentID);
    return "Error_CannotParseID";
  }
} catch (e) {
  new Notice("脚本错误 (MainTopicID): " + e.message);
  return "Error_ScriptFailed";
}