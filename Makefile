default:
		python hashes.py  > graph.dot

view:
		python hashes.py  > graph.dot && dot graph.dot -Tpng -o graph.png
		xdg-open graph.png
