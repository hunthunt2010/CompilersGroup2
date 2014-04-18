#Maria Deslis symbole table
#tutorial from eli.thegreenplace.net

def outer(aa)
	def inner()
		bb = 1
		return aa + bb + cc
	return inner

def describe_symbol(sym):
	def print_d(s, *args):
		prefix = ' ' * indent
		print(prefix + s, *args)

	assert isinstance(st, symtable.SymbolTable)
		print_d('Symtable: type=%s, id=%s, name=%s' % (
		st.get_type(), st.get_id(), st.get_name()))
		print_d('  nested:', st.is_nested())
		print_d('  has children:', st.has_children())
		print_d('  identifiers:', list(st.get_identifiers()))

	if recursive:
		for child_st in st.get_children():
			 describe_symtable(child_st, recursive, indent + 5)
