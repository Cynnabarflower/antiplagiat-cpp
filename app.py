import re
from difflib import SequenceMatcher
from flask import Flask, jsonify, request
import ftplib
import time

app = Flask(__name__);

keywords = '''
alignas
alignof
and
and_eq
asm
auto
bitand
bitor
bool
break
case
catch
char
char16_t
char32_t
class
compl
const
constexpr
const_cast
continue	
decltype
default
delete
do
double
dynamic_cast
else
enum
explicit
export
extern
false
float
for
friend
goto
if
inline
int
long
mutable	namespace
new
noexcept
not
not_eq
nullptr
operator
or
or_eq
private
protected
public
register
reinterpret_cast
return
short
signed
sizeof
static
static_assert
static_cast	struct
switch
template
this
thread_local
throw
true
try
typedef
typeid
typename
union
unsigned
using
virtual
void
volatile
wchar_t
while
xor
xor_eq
+
-
=
*
/
%
<
>
(
)
{
}
[
]
cin
cout
printf
'''.split()

all_ids = dict()
ids = []
unique_ids = []
count = 0
ratios = []

def foo2(s, unique_ids = True):
    i = len(all_ids)
    words = s.split()
    words = list(set(words))
    words.sort(key=lambda a: (-len(a), a))

    operator_s = ''

    for word in words:
        if word not in keywords:
            if s.count(word) == 1:
                s = s.replace(word, '')
            else:
                if word in all_ids:
                    s = s.replace(word, all_ids[word])
                else:
                    if unique_ids:
                        _id = f'ID{i}'
                        i += 1
                    else:
                        _id = 'ID'
                    s = s.replace(word, _id)
                    all_ids[word] = _id
                    # unique_ids[count].append(id)

        else:
            s = s.replace(word, 'kw')
            operator_s += ' '+word
    return [s, operator_s]

def foo1(s):
    unique_ids.append([])
    ids.append(dict())
    s += '\n'
    s = s.lower()
    s = re.sub(r'//[^\n\r]*[\n\r]', '', s)
    s = re.sub(r'#include[^\n\r\s]*[\n\r\s]', '', s)
    s = re.sub(r'/\*(.*?|\s)*\*/', '', s)
    s = re.sub(r'([+*/=<>();,{}@%\[\]:-])', r' \1 ', s)
    s = re.sub(r'"\s"', '', s)
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'\d+', 'n', s)
    return s

def countRatios(first, second):
    first[0] = re.sub(r'\s+', ' ', first[0])
    second[0] = re.sub(r'\s+', ' ', second[0])
    ratios.append(SequenceMatcher(None, first[0], second[0]).ratio())
    ratios.append(SequenceMatcher(None, re.sub(r'kw +', '', first[0]), re.sub(r'kw +', '', second[0])).ratio())
    ratios.append(SequenceMatcher(None, first[1], second[1]).ratio())


@app.route("/bot", methods=["POST"])
def response():
    
    try:
      ss = dict(request.form)['s1']
      ss1 = dict(request.form)['s2']


      ss = foo1(ss)
      ss1 = foo1(ss1)

      ratios.append(SequenceMatcher(None, ss, ss1).ratio())

      first = foo2(ss)
      second = foo2(ss1)
      countRatios(first, second)

      ids.clear()
      all_ids.clear()
      first = foo2(ss, unique_ids=False)
      second = foo2(ss1, unique_ids=False)
      countRatios(first, second)

      print(ratios)
      print(max(ratios))
    except Exception as e:
        print(str(e))
    return str(ratios)
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", )
