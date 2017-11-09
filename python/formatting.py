def badge(val):
  if val == 1.0:
    clazz = "badge alert-success"
  elif val > 0.5:
    clazz = "badge alert-warning"
  else:
    clazz = "badge alert-danger"
  return {
    "val": val,
    "class": clazz
    }
