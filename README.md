exception_list
==============

Has a customer ever given you a big IP list and then told you that these 3 IPs are excluded from scope.  What about if your tools stopped in the middle of a scan and you already have some results. 
If is very hard to figure out the remaining IPs left to scan from your original scope. This tool will generate a list of IPs left over from the scope.

'-s','--scope' List of IPs in scope. REQUIRED.

'-e', '--except' List of IPs already scanned or out of scope. REQUIRED.

'-v on', '--verbose on' Turn on verbose output. Must be set to on.

'-o', '--out' Output File. Default results will be written to newlist.txt.
