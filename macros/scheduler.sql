{# Get execution_date from the environment variable #}
{%- macro execution_date() -%}
    {%- set execution_date_str = env_var('EXECUTION_DATE', "none") -%}

    {%- if execution_date_str == "none" -%}
        {{ return(modules.datetime.datetime.now()) }}
    {%- else -%}
        {{ return(modules.datetime.datetime.fromisoformat(execution_date_str)) }}
    {%- endif -%}
{%- endmacro -%}

{# format datetime #}
{%- macro strftime(datetime, format) -%}
    {{- datetime.strftime(format) -}}
{%- endmacro -%}


{# Get date string #}
{%- macro ds() -%}
    {%- set execution_date = execution_date() -%}
    {{- execution_date.strftime("%Y-%m-%d") -}}
{%- endmacro -%}

{# Get date string without dashes #}
{%- macro ds_nodash() -%}
    {%- set execution_date = execution_date() -%}
    {{- execution_date.strftime("%Y%m%d") -}}
{%- endmacro -%}

{# Get date string after adding n days to execution_date  #}
{%- macro ds_add(n) -%}
    {%- set execution_date_with_n_days = (execution_date() + modules.datetime.timedelta(days=n)) -%}
    {{- execution_date_with_n_days.strftime("%Y-%m-%d") -}}
{%- endmacro -%}


{# Get timestamp string #}
{%- macro ts() -%}
    {%- set execution_date = execution_date() -%}
    {{- execution_date.strftime("%Y-%m-%dT%H:%M:%S+00:00") -}}
{%- endmacro -%}


{# Get timestamp string without dashes #}
{%- macro ts_nodash() -%}
    {%- set execution_date = execution_date() -%}
    {{- execution_date.strftime("%Y%m%dT%H%M%S") -}}
{%- endmacro -%}
