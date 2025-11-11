import re


def auto_expand_names(input_name):
  """Auto expand field[1-3] to field1, field2, field3.

  Args:
    input_name: a string pattern like field[1-3]

  Returns:
    a string list of the expanded names
  """
  flag = 1
  if input_name.endswith(']'):
    match_obj = re.match(r'([a-zA-Z_]+)\[([0-9]+)-([0-9]+)\]', input_name)
  else:
    flag = 2
    match_obj = re.match(r'([a-zA-Z_]+)\[([0-9]+)-([0-9]+)\]([a-zA-Z_]+)',
                         input_name)
  if match_obj:
    prefix = match_obj.group(1)
    sid = int(match_obj.group(2))
    eid = int(match_obj.group(3)) + 1
    if flag == 2:
      endfix = match_obj.group(4)
      input_name = ['%s%d%s' % (prefix, tid, endfix) for tid in range(sid, eid)]
    else:
      input_name = ['%s%d' % (prefix, tid) for tid in range(sid, eid)]

  else:
    input_name = [input_name]
  return input_name


print(auto_expand_names('bundle_adx_list_[0-14]'))
