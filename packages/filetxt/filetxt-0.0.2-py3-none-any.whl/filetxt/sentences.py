import re
import spacy

nlp = None
# spacy.load("en_core_web_sm")

def get_nlp():
	global nlp
	if nlp is None:
		config = getConfig()
		nlp = spacy.load(config.spacy_model_path)
	return nlp

def split_sentences(text: str):
    """
    中英文混合断句：
    - 英文部分：用 spaCy
    - 中文部分：用正则，支持引号/全角符号
    """
    # 英文先用 spaCy
	nlp = get_nlp()
    doc = nlp(text)
    english_sentences = [sent.text.strip() for sent in doc.sents]

    final_sentences = []
    
    # 中文句子结束符号（含全角/半角）
    chinese_splitter = re.compile(r"(.*?[。！？；!?…]+[”’」』》】）]?)")

    for sent in english_sentences:
        # 中文再细分
        parts = chinese_splitter.findall(sent)
        if parts:
            final_sentences.extend([p.strip() for p in parts if p.strip()])
            rest = chinese_splitter.sub("", sent).strip()
            if rest:
                final_sentences.append(rest)
        else:
            final_sentences.append(sent)

    return final_sentences


if __name__ == '__main__':
	# 示例
	text = "小明说：“今天下雨了！”但Mr. Smith说: No. 5 road is dry. 还有一句……OK?"
	print(split_sentences(text))

