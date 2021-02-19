-- The query looks inappropriate to test the macro.
-- But, it' better than nothing.
-- We can test at least if we can call the macro.
{% if already_exists() %}
SELECT 1
{% else %}
SELECT 2
{% endif %}