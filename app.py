# -*- coding: utf-8 -*-
"""
Created on Mon Oct 19 17:53:34 2026

@author: omarn
"""
import timeit,	tracemalloc
import streamlit as st

rtl_css = """
<style>
.rtl-text {
    direction: rtl;
    unicode-bidi: bidi-override;
    font-family: "Arial", sans-serif;
    font-size: 18px;
}
</style>
"""

# Inject CSS into Streamlit
st.markdown(rtl_css, unsafe_allow_html=True)
st.markdown("<style>body { direction: rtl; unicode-bidi: bidi-override; }</style>", unsafe_allow_html=True)


st.title("المقارنة المعيارية")
st.subheader("في بيئة التطوير بالبايثون بين:")
def record(code):
	start = timeit.default_timer()
	tracemalloc.start()
	exec(code)
	memory_usage = tracemalloc.get_traced_memory()
	tracemalloc.stop()
	end = timeit.default_timer()
	current, peak, diff = memory_usage[0]/ (1024**2), memory_usage[1]/ (1024**2), (memory_usage[1] - memory_usage[0]) / (1024**2) 
	fmt_stats = {#Could use the unpack method at the LHS as follows: (duration, value), (current,value), (peak,value), (diff,value)
#... then repack them using: dict([(duration, value), (current,value), (peak,value), (diff,value)])
#>> validated through interactive REPL.

			"مدة التنفيذ (بالمللي ثانية)": f"{(end-start)*1000:.3f}"	,
			"الحجم الحالي (بالميجا بايت)": f"{current:.6f}"			,
			"حجم الذروة (بالميجا بايت)": f"{peak:.3f}"				,
			#"memo_diff_MB": f"{diff:.6f}"  
			}
	return fmt_stats

		
col1_row1, col2_row1 = st.columns(2)
code_1_stat, code_2_stat = """{}""", """{}"""
if not "clicks" in st.session_state:
		st.session_state.clicks = [False,False]
def click_button(key):
    st.session_state.clicks[key-1] = True

with col1_row1:
		code_1 = st.text_area("استخدام أدوات خارجية (3rd-party):", key = "11")
		st.button("تشغيل",key=1, on_click=click_button, args=(1,))
		if st.session_state.clicks[1-1]:
			st.write(record(code_1))

with col2_row1:
		code_2 = st.text_area("استخدام الوحدات البرمجية المدمجة (built-in) أو أي مكتبة خارجية أخرى:", key = "22")

		# code_2_stat = record(
		# st.text_area("استخدام أدوات خارجية (3rd-party):")
		# )
		st.button("تشغيل",key=2, on_click=click_button, args=(2,))
		if st.session_state.clicks[2-1]:
			st.write(record(code_2))
        
with st.sidebar:
	st.title("أدوات قياس الأداء:\n#")
	st.markdown(
    '### <tt style="font-family: monospace; font-weight: normal;">`timeit` — قياس وقت تنفيذ مقتطفات برمجية </tt>', 
    unsafe_allow_html=True
)
	st.markdown("**الكود المصدري:** [Lib/timeit.py](https://github.com/python/cpython/blob/3.15/Lib/timeit.py)")
  # st.markdown('***')
	st.divider()
	st.markdown(
    '### <tt style="font-family: monospace; font-weight: normal;">`tracemalloc` — تتبُّع تخصيصات الذاكرة</tt>\n\n > :yellow[تشير الذاكرة «الحالية» (current memory) إلى الذاكرة التي يستخدمها الكود في الوقت الراهن، بينما تشير الذاكرة «القصوى» (peak memory) إلى الحد الأقصى من المساحة التي استهلكها البرنامج أثناء تنفيذه.]', 
    unsafe_allow_html=True
)
	st.markdown("**الكود المصدري:** [Lib/tracemalloc.py](https://github.com/python/cpython/blob/3.15/Lib/tracemalloc.py)")

st.markdown("""
<div class="rtl-text">\n
# لماذا تتفاوت أوقات التنفيذ؟
	تُرجع وحدة `timeit` في لغة بايثون قيمًا زمنية مختلفة في كل مرة يتم فيها التشغيل؛ \n
    فالأسباب التالية توضح أن زمن التنفيذ يُعد قياسًا فيزيائيًا يعتمد على العتاد ونظام التشغيل، \n
    وليس عملية حسابية حتمية النتائج.
• عمليات نظام التشغيل في الخلفية \n
>يدير نظام التشغيل باستمرار مئات المهام الخلفية، \nو
مقاطعات الشبكة، والخدمات التي تتنافس مع لغة "بايثون" (Python) على وقت المعالج (CPU). \n
• تغيير تردد المعالج (CPU Frequency Scaling) \n
>تقوم المعالجات الحديثة برفع أو خفض سرعة ساعتها ديناميكيًا \n	(على سبيل المثال، عبر تقنية Turbo Boost أو خفض السرعة بسبب الحرارة - thermal throttling) بناءً على درجة الحرارة، وحدود الطاقة، وعبء العمل الحالي. \n
• التخزين المؤقت في المعالج (CPU Caching) \n
>عند التشغيل لأول مرة، قد تُجلب البيانات من ذاكرة الوصول العشوائي (RAM) الرئيسية، وهي أبطأ نسبيًا. \n	أما في مرات التشغيل اللاحقة، فقد تكون تلك البيانات موجودة بالفعل في ذاكرة التخزين المؤقت فائقة السرعة للمعالج (L1/L2/L3)، مما يجعل تنفيذ الكود أسرع. \n
• تخصيص الذاكرة \n
> الرغم من أن أداة `timeit` تقوم بتعطيل "جامع القمامة" (garbage collector) في "بايثون" مؤقتًا أثناء الاختبار، \n إلا أن مدير الذاكرة في نظام التشغيل يظل يخصص صفحات الذاكرة ديناميكيًا، وهي عملية تستغرق فترات زمنية متفاوتة قليلاً.
	</div>""", unsafe_allow_html=True)
