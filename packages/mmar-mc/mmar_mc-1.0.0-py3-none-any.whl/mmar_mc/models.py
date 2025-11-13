from mmar_mapi import Content

FileName = str
FileData = tuple[FileName, bytes]
MessageData = tuple[Content | None, FileData | None]
