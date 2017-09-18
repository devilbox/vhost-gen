#!/usr/bin/env bash

set +e
set +u
#set -o pipefail

function get_random_el() {
	local arr=("${@}")
	local len="${#arr[@]}"

	random="$(( ( RANDOM % "${len}" )  + 1 ))"
	random="$(( random - 1))"

	echo ${arr[${random}]}
}


###
### Round 1 (Supported Options only)
###
declare -a args=(c p n t)
declare -a vals="(./ ./etc ./etc/templates ../ ../etc ../etc/templates ../../ ../../etc ../../etc/templates /etc /etc/vhost-gen /etc/vhost-gen/templates)"

for count in {1..2000}; do
	arg1="$( get_random_el "${args[@]}" )"
	arg2="$( get_random_el "${args[@]}" )"
	arg3="$( get_random_el "${args[@]}" )"
	arg4="$( get_random_el "${args[@]}" )"
	arg5="$( get_random_el "${args[@]}" )"

	val1="$( get_random_el "${vals[@]}" )"
	val2="$( get_random_el "${vals[@]}" )"
	val3="$( get_random_el "${vals[@]}" )"
	val4="$( get_random_el "${vals[@]}" )"
	val5="$( get_random_el "${vals[@]}" )"

	# 1
	cmd="../bin/vhost_gen.py -${arg1} ${val1}"
	printf "[%04d] %s\n" "${count}" "${cmd}"
	out="$( eval "${cmd}" 2>&1 || true )"
	if echo "${out}" | grep -qi "Traceback"; then
		echo "${out}"
		exit 1
	fi

	# 2
	cmd="../bin/vhost_gen.py -${arg1} ${val1} -${arg2} ${val2}"
	printf "[%04d] %s\n" "${count}" "${cmd}"
	out="$( eval "${cmd}" 2>&1 || true )"
	if echo "${out}" | grep -qi "Traceback"; then
		echo "${out}"
		exit 1
	fi

	# 3
	cmd="../bin/vhost_gen.py -${arg1} ${val1} -${arg2} ${val2} -${arg3} ${val3}"
	printf "[%04d] %s\n" "${count}" "${cmd}"
	out="$( eval "${cmd}" 2>&1 || true )"
	if echo "${out}" | grep -qi "Traceback"; then
		echo "${out}"
		exit 1
	fi

	# 4
	cmd="../bin/vhost_gen.py -${arg1} ${val1} -${arg2} ${val2} -${arg3} ${val3} -${arg4} ${val4}"
	printf "[%04d] %s\n" "${count}" "${cmd}"
	out="$( eval "${cmd}" 2>&1 || true )"
	if echo "${out}" | grep -qi "Traceback"; then
		echo "${out}"
		exit 1
	fi

	# 5
	cmd="../bin/vhost_gen.py -${arg1} ${val1} -${arg2} ${val2} -${arg3} ${val3} -${arg4} ${val4}  -${arg5} ${val5}"
	printf "[%04d] %s\n" "${count}" "${cmd}"
	out="$( eval "${cmd}" 2>&1 || true )"
	if echo "${out}" | grep -qi "Traceback"; then
		echo "${out}"
		exit 1
	fi
done


###
### Round 2 (Any Options)
###
declare -a args="(a b c d e f g h i j k l m n o p q r s t u v w x y z 0 1 2 3 4 5 6 7 8 9)"
declare -a vals="(c p n t -c -p -n -t -h -v ./ ./etc ./etc/templates ../ ../etc ../etc/templates ../../ ../../etc ../../etc/templates /etc /etc/vhost-gen /etc/vhost-gen/templates)"

for count in {1..2000}; do
	arg1="$( get_random_el "${args[@]}" )"
	arg2="$( get_random_el "${args[@]}" )"
	arg3="$( get_random_el "${args[@]}" )"
	arg4="$( get_random_el "${args[@]}" )"
	arg5="$( get_random_el "${args[@]}" )"

	val1="$( get_random_el "${vals[@]}" )"
	val2="$( get_random_el "${vals[@]}" )"
	val3="$( get_random_el "${vals[@]}" )"
	val4="$( get_random_el "${vals[@]}" )"
	val5="$( get_random_el "${vals[@]}" )"

	# 1
	cmd="../bin/vhost_gen.py -${arg1} ${val1}"
	printf "[%04d] %s\n" "${count}" "${cmd}"
	out="$( eval "${cmd}" 2>&1 || true )"
	if echo "${out}" | grep -qi "Traceback"; then
		echo "${out}"
		exit 1
	fi

	# 2
	cmd="../bin/vhost_gen.py -${arg1} ${val1} -${arg2} ${val2}"
	printf "[%04d] %s\n" "${count}" "${cmd}"
	out="$( eval "${cmd}" 2>&1 || true )"
	if echo "${out}" | grep -qi "Traceback"; then
		echo "${out}"
		exit 1
	fi

	# 3
	cmd="../bin/vhost_gen.py -${arg1} ${val1} -${arg2} ${val2} -${arg3} ${val3}"
	printf "[%04d] %s\n" "${count}" "${cmd}"
	out="$( eval "${cmd}" 2>&1 || true )"
	if echo "${out}" | grep -qi "Traceback"; then
		echo "${out}"
		exit 1
	fi

	# 4
	cmd="../bin/vhost_gen.py -${arg1} ${val1} -${arg2} ${val2} -${arg3} ${val3} -${arg4} ${val4}"
	printf "[%04d] %s\n" "${count}" "${cmd}"
	out="$( eval "${cmd}" 2>&1 || true )"
	if echo "${out}" | grep -qi "Traceback"; then
		echo "${out}"
		exit 1
	fi

	# 5
	cmd="../bin/vhost_gen.py -${arg1} ${val1} -${arg2} ${val2} -${arg3} ${val3} -${arg4} ${val4}  -${arg5} ${val5}"
	printf "[%04d] %s\n" "${count}" "${cmd}"
	out="$( eval "${cmd}" 2>&1 || true )"
	if echo "${out}" | grep -qi "Traceback"; then
		echo "${out}"
		exit 1
	fi
done
