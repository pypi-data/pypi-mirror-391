#!/bin/bash
# Bash completion script for imgctl

_imgctl_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # Основные команды
    local main_commands="servers nodes stacks components registries repositories logs version"
    
    # Глобальные параметры
    local global_options="--server -s --username -u --password -p --config -c --verbose -v --help -h"
    
    # Если это первое слово после imgctl
    if [[ ${COMP_CWORD} -eq 1 ]]; then
        COMPREPLY=($(compgen -W "${main_commands} ${global_options}" -- ${cur}))
        return 0
    fi
    
    # Если предыдущее слово --server или -s, предлагаем серверы
    if [[ "${prev}" == "--server" || "${prev}" == "-s" ]]; then
        local servers=$(_imgctl_get_servers)
        COMPREPLY=($(compgen -W "${servers}" -- ${cur}))
        return 0
    fi
    
    # Получаем команду (учитываем глобальные параметры)
    local cmd=""
    local cmd_pos=1
    
    # Ищем команду, пропуская глобальные параметры
    while [[ $cmd_pos -lt ${#COMP_WORDS[@]} ]]; do
        local word="${COMP_WORDS[$cmd_pos]}"
        if [[ "$word" =~ ^(--server|-s|--username|-u|--password|-p|--config|-c|--verbose|-v|--help|-h)$ ]]; then
            # Это глобальный параметр, пропускаем его и следующее слово (если есть)
            ((cmd_pos++))
            if [[ $cmd_pos -lt ${#COMP_WORDS[@]} ]]; then
                ((cmd_pos++))
            fi
        else
            # Это команда
            cmd="$word"
            break
        fi
    done
    
    # Если команда не найдена, предлагаем команды
    if [[ -z "$cmd" ]]; then
        COMPREPLY=($(compgen -W "${main_commands}" -- ${cur}))
        return 0
    fi
    
    case "${cmd}" in
        components)
            _imgctl_components_completion
            ;;
        stacks)
            _imgctl_stacks_completion
            ;;
        nodes)
            _imgctl_nodes_completion
            ;;
        logs)
            _imgctl_logs_completion
            ;;
        servers)
            _imgctl_servers_completion
            ;;
        registries)
            _imgctl_registries_completion
            ;;
        repositories)
            _imgctl_repositories_completion
            ;;
    esac
}

_imgctl_components_completion() {
    local cur prev
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # Подкоманды components
    local subcommands="list get start stop tags upgrade"
    
    # Определяем позицию подкоманды (учитываем глобальные параметры)
    local subcmd_pos=2
    local i=1
    while [[ $i -lt ${#COMP_WORDS[@]} ]]; do
        local word="${COMP_WORDS[$i]}"
        if [[ "$word" =~ ^(--server|-s|--username|-u|--password|-p|--config|-c|--verbose|-v|--help|-h)$ ]]; then
            # Это глобальный параметр, пропускаем его и следующее слово (если есть)
            ((i++))
            if [[ $i -lt ${#COMP_WORDS[@]} ]]; then
                ((i++))
            fi
        else
            # Это команда, следующее слово - подкоманда
            subcmd_pos=$((i + 1))
            break
        fi
    done
    
    # Если это позиция подкоманды
    if [[ ${COMP_CWORD} -eq ${subcmd_pos} ]]; then
        COMPREPLY=($(compgen -W "${subcommands}" -- ${cur}))
        return 0
    fi
    
    local subcmd="${COMP_WORDS[${subcmd_pos}]}"
    
    case "${subcmd}" in
        list)
            _imgctl_components_list_completion
            ;;
        get|start|stop)
            _imgctl_components_name_completion
            ;;
        tags)
            _imgctl_components_tags_completion
            ;;
        upgrade)
            _imgctl_components_upgrade_completion
            ;;
    esac
}

_imgctl_components_list_completion() {
    local cur prev
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # Опции для components list
    local options="--limit -l --no-cache --columns --filter --no-headers --output -o --verbose -v --help"
    
    # Если предыдущее слово --columns, предлагаем колонки
    if [[ "${prev}" == "--columns" ]]; then
        local columns="NAME NAMESPACE STACK IMAGE TAG STACK_VERSION STATUS REPLICAS PORTS UPDATED CREATED REPO COMMIT ADMIN_MODE RUN_APP SHOW_ADMIN_MODE OFF NETWORKS ENV"
        COMPREPLY=($(compgen -W "${columns}" -- ${cur}))
        return 0
    fi
    
    # Если предыдущее слово --output, предлагаем форматы
    if [[ "${prev}" == "--output" || "${prev}" == "-o" ]]; then
        local formats="json yaml tsv"
        COMPREPLY=($(compgen -W "${formats}" -- ${cur}))
        return 0
    fi
    
    # Иначе предлагаем опции
    COMPREPLY=($(compgen -W "${options}" -- ${cur}))
}

_imgctl_components_name_completion() {
    local cur
    cur="${COMP_WORDS[COMP_CWORD]}"
    
    # Определяем позицию аргумента компонента (учитываем глобальные параметры)
    local component_arg_pos=3
    local i=1
    local cmd_found=false
    while [[ $i -lt ${#COMP_WORDS[@]} ]]; do
        local word="${COMP_WORDS[$i]}"
        if [[ "$word" =~ ^(--server|-s|--username|-u|--password|-p|--config|-c|--verbose|-v|--help|-h)$ ]]; then
            # Это глобальный параметр, пропускаем его и следующее слово (если есть)
            ((i++))
            if [[ $i -lt ${#COMP_WORDS[@]} ]]; then
                ((i++))
            fi
        else
            # Это команда
            if [[ "$cmd_found" == false ]]; then
                cmd_found=true
                # Следующее слово - подкоманда, еще следующее - аргумент
                component_arg_pos=$((i + 2))
            fi
            ((i++))
        fi
    done
    
    # Если уже есть аргумент компонента, не предлагаем больше
    if [[ ${COMP_CWORD} -gt ${component_arg_pos} ]]; then
        COMPREPLY=()
        return 0
    fi
    
    # Получаем имена компонентов
    local components=$(_imgctl_get_components)
    COMPREPLY=($(compgen -W "${components}" -- ${cur}))
}

_imgctl_components_tags_completion() {
    local cur prev
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # Опции для components tags
    local options="--limit -l --no-cache --verbose -v --help"
    
    # Определяем позицию аргумента компонента (учитываем глобальные параметры)
    local component_arg_pos=3
    local i=1
    local cmd_found=false
    while [[ $i -lt ${#COMP_WORDS[@]} ]]; do
        local word="${COMP_WORDS[$i]}"
        if [[ "$word" =~ ^(--server|-s|--username|-u|--password|-p|--config|-c|--verbose|-v|--help|-h)$ ]]; then
            # Это глобальный параметр, пропускаем его и следующее слово (если есть)
            ((i++))
            if [[ $i -lt ${#COMP_WORDS[@]} ]]; then
                ((i++))
            fi
        else
            # Это команда
            if [[ "$cmd_found" == false ]]; then
                cmd_found=true
                # Следующее слово - подкоманда, еще следующее - аргумент
                component_arg_pos=$((i + 2))
            fi
            ((i++))
        fi
    done
    
    # Если это позиция аргумента компонента
    if [[ ${COMP_CWORD} -eq ${component_arg_pos} ]]; then
        local components=$(_imgctl_get_components)
        COMPREPLY=($(compgen -W "${components}" -- ${cur}))
        return 0
    fi
    
    # Если уже есть аргумент компонента, предлагаем опции
    if [[ ${COMP_CWORD} -gt ${component_arg_pos} ]]; then
        COMPREPLY=($(compgen -W "${options}" -- ${cur}))
        return 0
    fi
    
    # Иначе предлагаем опции
    COMPREPLY=($(compgen -W "${options}" -- ${cur}))
}

_imgctl_components_upgrade_completion() {
    local cur prev
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # Опции для components upgrade
    local options="--from-file --check --dry-run --all --verbose -v --filter --to-tag --confirm --force --no-cache --no-headers --export-current --export-latest --export-upgradable --help"
    
    # Если предыдущее слово --from-file, предлагаем файлы
    if [[ "${prev}" == "--from-file" ]]; then
        COMPREPLY=($(compgen -f -- ${cur}))
        return 0
    fi
    
    # Если предыдущее слово --filter, предлагаем фильтры
    if [[ "${prev}" == "--filter" ]]; then
        local filters="STATUS= NAMESPACE= NAME= STACK= IMAGE= TAG="
        COMPREPLY=($(compgen -W "${filters}" -- ${cur}))
        return 0
    fi
    
    # Если предыдущее слово --to-tag, не предлагаем ничего (пользователь должен ввести тег)
    if [[ "${prev}" == "--to-tag" ]]; then
        COMPREPLY=()
        return 0
    fi
    
    # Если текущее слово начинается с - или --, всегда предлагаем опции
    if [[ "${cur}" =~ ^- ]]; then
        COMPREPLY=($(compgen -W "${options}" -- ${cur}))
        return 0
    fi
    
    # Проверяем, были ли уже указаны опции, которые требуют аргументов или являются флагами
    # Если предыдущее слово - опция, которая не требует аргумента, продолжаем
    local flag_options="--check --dry-run --all --confirm --force --no-cache --no-headers --export-current --export-latest --export-upgradable --verbose -v --help"
    if [[ " ${flag_options} " =~ " ${prev} " ]]; then
        # Предыдущее слово - флаг, текущее может быть еще один аргумент или опция
        # Предлагаем и компоненты и опции
        local components=$(_imgctl_get_components)
        local all_suggestions="${options} ${components}"
        COMPREPLY=($(compgen -W "${all_suggestions}" -- ${cur}))
        return 0
    fi
    
    # Если это позиция аргумента компонента (не опция)
    # Предлагаем компоненты, но также можно предложить опции если они еще не использованы
    local components=$(_imgctl_get_components)
    COMPREPLY=($(compgen -W "${components} ${options}" -- ${cur}))
}

_imgctl_stacks_completion() {
    local cur prev
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # Подкоманды stacks
    local subcommands="list get template"
    
    # Если это второе слово после stacks
    if [[ ${COMP_CWORD} -eq 2 ]]; then
        COMPREPLY=($(compgen -W "${subcommands}" -- ${cur}))
        return 0
    fi
    
    local subcmd="${COMP_WORDS[2]}"
    
    case "${subcmd}" in
        list)
            _imgctl_stacks_list_completion
            ;;
        get)
            _imgctl_stacks_name_completion
            ;;
        template)
            _imgctl_stacks_template_completion
            ;;
    esac
}

_imgctl_stacks_list_completion() {
    local cur prev
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # Опции для stacks list
    local options="--columns --filter --limit -l --no-headers --output -o --help"
    
    # Если предыдущее слово --columns, предлагаем колонки
    if [[ "${prev}" == "--columns" ]]; then
        local columns="NAME NAMESPACE VERSION STATUS REPO COMMIT TIME TAG PARAMS COMPONENTS"
        COMPREPLY=($(compgen -W "${columns}" -- ${cur}))
        return 0
    fi
    
    # Если предыдущее слово --output, предлагаем форматы
    if [[ "${prev}" == "--output" || "${prev}" == "-o" ]]; then
        local formats="json yaml tsv"
        COMPREPLY=($(compgen -W "${formats}" -- ${cur}))
        return 0
    fi
    
    # Иначе предлагаем опции
    COMPREPLY=($(compgen -W "${options}" -- ${cur}))
}

_imgctl_stacks_name_completion() {
    local cur
    cur="${COMP_WORDS[COMP_CWORD]}"
    
    # Получаем имена стеков
    local stacks=$(_imgctl_get_stacks)
    COMPREPLY=($(compgen -W "${stacks}" -- ${cur}))
}

# _imgctl_stacks_deploy_completion() {
#     local cur prev
#     cur="${COMP_WORDS[COMP_CWORD]}"
#     prev="${COMP_WORDS[COMP_CWORD-1]}"
#     
#     # Опции для stacks deploy
#     local options="--repository --git-ref --param --help"
#     
#     # Если предыдущее слово --repository, предлагаем репозитории
#     if [[ "${prev}" == "--repository" ]]; then
#         local repos=$(_imgctl_get_repositories)
#         COMPREPLY=($(compgen -W "${repos}" -- ${cur}))
#         return 0
#     fi
#     
#     # Иначе предлагаем опции
#     COMPREPLY=($(compgen -W "${options}" -- ${cur}))
# }

_imgctl_stacks_template_completion() {
    local cur prev
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # Опции для stacks template
    local options="--diff --no-cache --no-headers --verbose --help"
    
    # Если предыдущее слово --diff, предлагаем commit'ы (пока пусто)
    if [[ "${prev}" == "--diff" ]]; then
        COMPREPLY=()
        return 0
    fi
    
    # Если это третий аргумент (после stacks template), предлагаем имена стеков
    if [[ ${COMP_CWORD} -eq 3 ]]; then
        local stacks=$(_imgctl_get_stacks)
        COMPREPLY=($(compgen -W "${stacks}" -- ${cur}))
        return 0
    fi
    
    # Если это четвертый аргумент и предыдущее не --diff, предлагаем commit'ы (пока пусто)
    if [[ ${COMP_CWORD} -eq 4 && "${prev}" != "--diff" ]]; then
        COMPREPLY=()
        return 0
    fi
    
    # Иначе предлагаем опции
    COMPREPLY=($(compgen -W "${options}" -- ${cur}))
}

_imgctl_nodes_completion() {
    local cur prev
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # Подкоманды nodes
    local subcommands="list get"
    
    # Если это второе слово после nodes
    if [[ ${COMP_CWORD} -eq 2 ]]; then
        COMPREPLY=($(compgen -W "${subcommands}" -- ${cur}))
        return 0
    fi
    
    local subcmd="${COMP_WORDS[2]}"
    
    case "${subcmd}" in
        list)
            _imgctl_nodes_list_completion
            ;;
        get)
            _imgctl_nodes_name_completion
            ;;
    esac
}

_imgctl_nodes_list_completion() {
    local cur prev
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # Опции для nodes list
    local options="--columns --filter --no-headers --output -o --help"
    
    # Если предыдущее слово --columns, предлагаем колонки
    if [[ "${prev}" == "--columns" ]]; then
        local columns="NAME IP ROLE AVAILABILITY STATUS DC DOCKER_VERSION TOTAL_MEMORY SSH_PORT SSH_USER EXTERNAL_URL ID"
        COMPREPLY=($(compgen -W "${columns}" -- ${cur}))
        return 0
    fi
    
    # Если предыдущее слово --output, предлагаем форматы
    if [[ "${prev}" == "--output" || "${prev}" == "-o" ]]; then
        local formats="json yaml tsv"
        COMPREPLY=($(compgen -W "${formats}" -- ${cur}))
        return 0
    fi
    
    # Иначе предлагаем опции
    COMPREPLY=($(compgen -W "${options}" -- ${cur}))
}

_imgctl_nodes_name_completion() {
    local cur
    cur="${COMP_WORDS[COMP_CWORD]}"
    
    # Определяем позицию аргумента ноды (учитываем глобальные параметры)
    local node_arg_pos=3
    local i=1
    while [[ $i -lt ${#COMP_WORDS[@]} ]]; do
        local word="${COMP_WORDS[$i]}"
        if [[ "$word" =~ ^(--server|-s|--username|-u|--password|-p|--config|-c|--verbose|-v|--help|-h)$ ]]; then
            # Это глобальный параметр, пропускаем его и следующее слово (если есть)
            ((i++))
            if [[ $i -lt ${#COMP_WORDS[@]} ]]; then
                ((i++))
            fi
        else
            # Это команда, следующее слово - подкоманда, еще следующее - аргумент
            node_arg_pos=$((i + 2))
            break
        fi
    done
    
    # Если уже есть аргумент ноды, не предлагаем больше
    if [[ ${COMP_CWORD} -gt ${node_arg_pos} ]]; then
        COMPREPLY=()
        return 0
    fi
    
    # Получаем имена нод
    local nodes=$(_imgctl_get_nodes)
    COMPREPLY=($(compgen -W "${nodes}" -- ${cur}))
}

_imgctl_logs_completion() {
    local cur prev
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # Опции для logs
    local options="--browser --follow -f --lines -l --level --tail -t --since --no-cache --help"
    
    # Если предыдущее слово --level, предлагаем уровни
    if [[ "${prev}" == "--level" || "${prev}" == "-l" ]]; then
        local levels="ERROR WARN INFO DEBUG"
        COMPREPLY=($(compgen -W "${levels}" -- ${cur}))
        return 0
    fi
    
    # Если это не опция, предлагаем имена компонентов
    if [[ "${cur}" != -* ]]; then
        local components=$(_imgctl_get_components)
        COMPREPLY=($(compgen -W "${components}" -- ${cur}))
        return 0
    fi
    
    # Иначе предлагаем опции
    COMPREPLY=($(compgen -W "${options}" -- ${cur}))
}

_imgctl_servers_completion() {
    local cur prev
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # Подкоманды servers
    local subcommands="list add update remove set-default get test cache"
    
    # Если это второе слово после servers
    if [[ ${COMP_CWORD} -eq 2 ]]; then
        COMPREPLY=($(compgen -W "${subcommands}" -- ${cur}))
        return 0
    fi
    
    local subcmd="${COMP_WORDS[2]}"
    
    case "${subcmd}" in
        list)
            _imgctl_servers_list_completion
            ;;
        remove|set-default|get|test)
            _imgctl_servers_name_completion
            ;;
        add)
            _imgctl_servers_add_completion
            ;;
        update)
            _imgctl_servers_update_completion
            ;;
        cache)
            _imgctl_servers_cache_completion
            ;;
    esac
}

_imgctl_servers_list_completion() {
    local cur prev
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # Опции для servers list
    local options="--show-passwords --columns --filter --no-headers --output -o --help"
    
    # Если предыдущее слово --columns, предлагаем колонки
    if [[ "${prev}" == "--columns" ]]; then
        local columns="NAME URL USERNAME DESCRIPTION DEFAULT PASSWORD"
        COMPREPLY=($(compgen -W "${columns}" -- ${cur}))
        return 0
    fi
    
    # Если предыдущее слово --output, предлагаем форматы
    if [[ "${prev}" == "--output" || "${prev}" == "-o" ]]; then
        local formats="json yaml tsv"
        COMPREPLY=($(compgen -W "${formats}" -- ${cur}))
        return 0
    fi
    
    # Иначе предлагаем опции
    COMPREPLY=($(compgen -W "${options}" -- ${cur}))
}

_imgctl_servers_name_completion() {
    local cur
    cur="${COMP_WORDS[COMP_CWORD]}"
    
    # Получаем имена серверов
    local servers=$(_imgctl_get_servers)
    COMPREPLY=($(compgen -W "${servers}" -- ${cur}))
}

_imgctl_servers_add_completion() {
    local cur prev
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # Опции для servers add
    local options="--url --username --password --description --default --ttl --help"
    COMPREPLY=($(compgen -W "${options}" -- ${cur}))
}

_imgctl_servers_update_completion() {
    local cur prev
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # Опции для servers update
    local options="--url --username --password --description --default --ttl --help"
    COMPREPLY=($(compgen -W "${options}" -- ${cur}))
}

_imgctl_servers_cache_completion() {
    local cur prev
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # Подкоманды cache
    local subcommands="show set reset"
    
    # Если это третье слово после servers cache
    if [[ ${COMP_CWORD} -eq 3 ]]; then
        COMPREPLY=($(compgen -W "${subcommands}" -- ${cur}))
        return 0
    fi
    
    local subcmd="${COMP_WORDS[3]}"
    
    case "${subcmd}" in
        show)
            local options="--server -s --format --help"
            COMPREPLY=($(compgen -W "${options}" -- ${cur}))
            ;;
        set)
            local options="--server -s --help"
            COMPREPLY=($(compgen -W "${options}" -- ${cur}))
            ;;
        reset)
            local options="--server -s --help"
            COMPREPLY=($(compgen -W "${options}" -- ${cur}))
            ;;
    esac
}

_imgctl_registries_completion() {
    local cur prev
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # Подкоманды registries
    local subcommands="list get"
    
    # Если это второе слово после registries
    if [[ ${COMP_CWORD} -eq 2 ]]; then
        COMPREPLY=($(compgen -W "${subcommands}" -- ${cur}))
        return 0
    fi
    
    local subcmd="${COMP_WORDS[2]}"
    
    case "${subcmd}" in
        list)
            _imgctl_registries_list_completion
            ;;
        get)
            _imgctl_registries_name_completion
            ;;
    esac
}

_imgctl_registries_list_completion() {
    local cur
    cur="${COMP_WORDS[COMP_CWORD]}"
    
    # Опции для registries list
    local options="--no-headers --help"
    COMPREPLY=($(compgen -W "${options}" -- ${cur}))
}

_imgctl_registries_name_completion() {
    local cur
    cur="${COMP_WORDS[COMP_CWORD]}"
    
    # Определяем позицию аргумента реестра (учитываем глобальные параметры)
    local registry_arg_pos=3
    local i=1
    while [[ $i -lt ${#COMP_WORDS[@]} ]]; do
        local word="${COMP_WORDS[$i]}"
        if [[ "$word" =~ ^(--server|-s|--username|-u|--password|-p|--config|-c|--verbose|-v|--help|-h)$ ]]; then
            # Это глобальный параметр, пропускаем его и следующее слово (если есть)
            ((i++))
            if [[ $i -lt ${#COMP_WORDS[@]} ]]; then
                ((i++))
            fi
        else
            # Это команда, следующее слово - подкоманда, еще следующее - аргумент
            registry_arg_pos=$((i + 2))
            break
        fi
    done
    
    # Если уже есть аргумент реестра, не предлагаем больше
    if [[ ${COMP_CWORD} -gt ${registry_arg_pos} ]]; then
        COMPREPLY=()
        return 0
    fi
    
    # Получаем имена реестров
    local registries=$(_imgctl_get_registries)
    COMPREPLY=($(compgen -W "${registries}" -- ${cur}))
}

_imgctl_repositories_completion() {
    local cur prev
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # Подкоманды repositories
    local subcommands="list get"
    
    # Если это второе слово после repositories
    if [[ ${COMP_CWORD} -eq 2 ]]; then
        COMPREPLY=($(compgen -W "${subcommands}" -- ${cur}))
        return 0
    fi
    
    local subcmd="${COMP_WORDS[2]}"
    
    case "${subcmd}" in
        list)
            _imgctl_repositories_list_completion
            ;;
        get)
            _imgctl_repositories_name_completion
            ;;
    esac
}

_imgctl_repositories_list_completion() {
    local cur
    cur="${COMP_WORDS[COMP_CWORD]}"
    
    # Опции для repositories list
    local options="--no-headers --help"
    COMPREPLY=($(compgen -W "${options}" -- ${cur}))
}

_imgctl_repositories_name_completion() {
    local cur
    cur="${COMP_WORDS[COMP_CWORD]}"
    
    # Определяем позицию аргумента репозитория (учитываем глобальные параметры)
    local repository_arg_pos=3
    local i=1
    while [[ $i -lt ${#COMP_WORDS[@]} ]]; do
        local word="${COMP_WORDS[$i]}"
        if [[ "$word" =~ ^(--server|-s|--username|-u|--password|-p|--config|-c|--verbose|-v|--help|-h)$ ]]; then
            # Это глобальный параметр, пропускаем его и следующее слово (если есть)
            ((i++))
            if [[ $i -lt ${#COMP_WORDS[@]} ]]; then
                ((i++))
            fi
        else
            # Это команда, следующее слово - подкоманда, еще следующее - аргумент
            repository_arg_pos=$((i + 2))
            break
        fi
    done
    
    # Если уже есть аргумент репозитория, не предлагаем больше
    if [[ ${COMP_CWORD} -gt ${repository_arg_pos} ]]; then
        COMPREPLY=()
        return 0
    fi
    
    # Получаем имена репозиториев
    local repositories=$(_imgctl_get_repositories)
    COMPREPLY=($(compgen -W "${repositories}" -- ${cur}))
}

# Функции для получения данных через Python
_imgctl_get_server_name() {
    # Извлекаем имя сервера из аргументов командной строки
    local server_name=""
    local i=0
    while [[ $i -lt ${#COMP_WORDS[@]} ]]; do
        if [[ "${COMP_WORDS[$i]}" == "--server" || "${COMP_WORDS[$i]}" == "-s" ]]; then
            # Следующий аргумент - имя сервера или URL
            if [[ $((i+1)) -lt ${#COMP_WORDS[@]} ]]; then
                server_name="${COMP_WORDS[$((i+1))]}"
                break
            fi
        fi
        ((i++))
    done
    
    # Если сервер не найден в аргументах, проверяем переменные окружения
    if [[ -z "$server_name" ]]; then
        server_name="${IMG_SERVER}"
    fi
    
    echo "$server_name"
}

_imgctl_get_components() {
    local server_name=$(_imgctl_get_server_name)
    python3 -c "
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath('$0')))
from core.completion import CompletionManager
cm = CompletionManager(server_name='$server_name')
components = cm.get_components()
print(' '.join(components))
" 2>/dev/null || echo ""
}

_imgctl_get_stacks() {
    local server_name=$(_imgctl_get_server_name)
    python3 -c "
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath('$0')))
from core.completion import CompletionManager
cm = CompletionManager(server_name='$server_name')
stacks = cm.get_stacks()
print(' '.join(stacks))
" 2>/dev/null || echo ""
}

_imgctl_get_nodes() {
    local server_name=$(_imgctl_get_server_name)
    python3 -c "
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath('$0')))
from core.completion import CompletionManager
cm = CompletionManager(server_name='$server_name')
nodes = cm.get_nodes()
print(' '.join(nodes))
" 2>/dev/null || echo ""
}

_imgctl_get_registries() {
    local server_name=$(_imgctl_get_server_name)
    python3 -c "
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath('$0')))
from core.completion import CompletionManager
cm = CompletionManager(server_name='$server_name')
registries = cm.get_registries()
print(' '.join(registries))
" 2>/dev/null || echo ""
}

_imgctl_get_repositories() {
    local server_name=$(_imgctl_get_server_name)
    python3 -c "
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath('$0')))
from core.completion import CompletionManager
cm = CompletionManager(server_name='$server_name')
repositories = cm.get_repositories()
print(' '.join(repositories))
" 2>/dev/null || echo ""
}

_imgctl_get_servers() {
    python3 -c "
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath('$0')))
from core.completion import CompletionManager
cm = CompletionManager()
servers = cm.get_servers()
print(' '.join(servers))
" 2>/dev/null || echo ""
}

_imgctl_get_namespaces() {
    local server_name=$(_imgctl_get_server_name)
    python3 -c "
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath('$0')))
from core.completion import CompletionManager
cm = CompletionManager(server_name='$server_name')
namespaces = cm.get_namespaces()
print(' '.join(namespaces))
" 2>/dev/null || echo ""
}

# Функции управления completion
_imgctl_completion_help() {
    echo "imgctl-completion.bash - Bash completion для imgctl"
    echo ""
    echo "Использование:"
    echo "  $0 install [--bashrc] [--profile] [--zsh]  - Установить completion"
    echo "  $0 test                                    - Протестировать completion"
    echo "  $0 uninstall                               - Удалить completion"
    echo "  $0 help                                    - Показать эту справку"
    echo ""
    echo "Примеры:"
    echo "  $0 install --bashrc                        - Установить в ~/.bashrc"
    echo "  $0 install --profile --zsh                 - Установить в ~/.bash_profile и создать zsh версию"
    echo ""
    echo "Для активации completion добавьте в ~/.bashrc:"
    echo "  source $(realpath "$0")"
}

_imgctl_completion_install() {
    local bashrc=false
    local profile=false
    local zsh=false
    
    # Парсим аргументы
    while [[ $# -gt 0 ]]; do
        case $1 in
            --bashrc)
                bashrc=true
                shift
                ;;
            --profile)
                profile=true
                shift
                ;;
            --zsh)
                zsh=true
                shift
                ;;
            *)
                echo "Неизвестный параметр: $1"
                _imgctl_completion_help
                exit 1
                ;;
        esac
    done
    
    # Если не указаны опции, устанавливаем в bashrc по умолчанию
    if [[ "$bashrc" == false && "$profile" == false ]]; then
        bashrc=true
    fi
    
    echo "Установка bash completion для imgctl..."
    
    # Создаем директорию для completion
    local completion_dir="$HOME/.local/share/imgctl"
    mkdir -p "$completion_dir"
    
    # Копируем скрипт
    local target_script="$completion_dir/imgctl-completion.bash"
    cp "$0" "$target_script"
    chmod +x "$target_script"
    
    echo "✓ Скрипт completion установлен в $target_script"
    
    # Добавляем в bashrc
    if [[ "$bashrc" == true ]]; then
        _imgctl_add_to_shell_config "$HOME/.bashrc" "$target_script"
    fi
    
    # Добавляем в bash_profile
    if [[ "$profile" == true ]]; then
        _imgctl_add_to_shell_config "$HOME/.bash_profile" "$target_script"
    fi
    
    # Создаем zsh completion
    if [[ "$zsh" == true ]]; then
        _imgctl_create_zsh_completion "$target_script"
    fi
    
    echo ""
    echo "Для активации completion выполните:"
    echo "  source $target_script"
    echo "Или перезапустите терминал"
}

_imgctl_completion_test() {
    echo "Тестирование bash completion для imgctl..."
    echo ""
    
    # Проверяем, что функция зарегистрирована
    if complete -p imgctl >/dev/null 2>&1; then
        echo "✓ Completion зарегистрирован для imgctl"
    else
        echo "✗ Completion не зарегистрирован для imgctl"
        echo "  Выполните: source $0"
        return 1
    fi
    
    # Тестируем основные команды
    echo ""
    echo "Тестирование автодополнения команд:"
    COMP_WORDS=(imgctl ''); COMP_CWORD=1; _imgctl_completion
    echo "  imgctl <TAB> → $(printf '%s ' "${COMPREPLY[@]}")"
    
    # Тестируем подкоманды
    echo ""
    echo "Тестирование автодополнения подкоманд:"
    COMP_WORDS=(imgctl components ''); COMP_CWORD=2; _imgctl_completion
    echo "  imgctl components <TAB> → $(printf '%s ' "${COMPREPLY[@]}")"
    
    # Тестируем параметры
    echo ""
    echo "Тестирование автодополнения параметров:"
    COMP_WORDS=(imgctl components list --); COMP_CWORD=3; _imgctl_completion
    echo "  imgctl components list --<TAB> → $(printf '%s ' "${COMPREPLY[@]}")"
    
    # Тестируем получение данных через Python
    echo ""
    echo "Тестирование получения данных из API:"
    
    local components=$(_imgctl_get_components)
    if [[ -n "$components" ]]; then
        local count=$(echo "$components" | wc -w)
        echo "  ✓ Компоненты: $count найдено"
        echo "    Примеры: $(echo "$components" | tr ' ' '\n' | head -3 | tr '\n' ' ')"
    else
        echo "  ✗ Компоненты: не удалось получить данные"
    fi
    
    local stacks=$(_imgctl_get_stacks)
    if [[ -n "$stacks" ]]; then
        local count=$(echo "$stacks" | wc -w)
        echo "  ✓ Стеки: $count найдено"
        echo "    Примеры: $(echo "$stacks" | tr ' ' '\n' | head -3 | tr '\n' ' ')"
    else
        echo "  ✗ Стеки: не удалось получить данные"
    fi
    
    local servers=$(_imgctl_get_servers)
    if [[ -n "$servers" ]]; then
        local count=$(echo "$servers" | wc -w)
        echo "  ✓ Серверы: $count найдено"
        echo "    Примеры: $(echo "$servers" | tr ' ' '\n' | head -3 | tr '\n' ' ')"
    else
        echo "  ✗ Серверы: не удалось получить данные"
    fi
    
    echo ""
    echo "✓ Тестирование завершено!"
}

_imgctl_completion_uninstall() {
    echo "Удаление bash completion для imgctl..."
    
    # Удаляем скрипт
    local completion_dir="$HOME/.local/share/imgctl"
    local target_script="$completion_dir/imgctl-completion.bash"
    
    if [[ -f "$target_script" ]]; then
        rm -f "$target_script"
        echo "✓ Скрипт completion удален"
    else
        echo "! Скрипт completion не найден"
    fi
    
    # Удаляем zsh версию
    local zsh_script="$completion_dir/imgctl-completion.zsh"
    if [[ -f "$zsh_script" ]]; then
        rm -f "$zsh_script"
        echo "✓ Zsh completion удален"
    fi
    
    # Удаляем из конфигурационных файлов
    for config_file in ".bashrc" ".bash_profile"; do
        local config_path="$HOME/$config_file"
        if [[ -f "$config_path" ]]; then
            _imgctl_remove_from_shell_config "$config_path" "imgctl-completion.bash"
        fi
    done
    
    echo "✓ Completion удален"
}

_imgctl_add_to_shell_config() {
    local config_path="$1"
    local script_path="$2"
    
    # Создаем файл если не существует
    if [[ ! -f "$config_path" ]]; then
        touch "$config_path"
    fi
    
    # Проверяем, не добавлен ли уже
    if grep -q "imgctl-completion.bash" "$config_path" 2>/dev/null; then
        echo "! Completion уже добавлен в $config_path"
        return
    fi
    
    # Добавляем в конец файла
    {
        echo ""
        echo "# imgctl completion"
        echo "if [ -f $script_path ]; then"
        echo "    source $script_path"
        echo "fi"
    } >> "$config_path"
    
    echo "✓ Completion добавлен в $config_path"
}

_imgctl_remove_from_shell_config() {
    local config_path="$1"
    local script_name="$2"
    
    if [[ ! -f "$config_path" ]]; then
        return
    fi
    
    # Создаем временный файл
    local temp_file=$(mktemp)
    
    # Фильтруем строки, связанные с completion
    local skip_next=false
    while IFS= read -r line; do
        if [[ "$line" == *"$script_name"* ]]; then
            skip_next=true
            continue
        elif [[ "$skip_next" == true && "$line" == "fi" ]]; then
            skip_next=false
            continue
        elif [[ "$skip_next" == true ]]; then
            continue
        else
            echo "$line" >> "$temp_file"
        fi
    done < "$config_path"
    
    # Заменяем оригинальный файл
    mv "$temp_file" "$config_path"
    
    echo "✓ Completion удален из $config_path"
}

_imgctl_create_zsh_completion() {
    local bash_script="$1"
    local zsh_script="${bash_script%.bash}.zsh"
    
    # Читаем bash скрипт и адаптируем для zsh
    local bash_content=$(cat "$bash_script")
    
    # Заменяем bash-специфичные функции на zsh
    local zsh_content=$(echo "$bash_content" | sed 's/complete -F _imgctl_completion imgctl/compdef _imgctl_completion imgctl/')
    
    # Добавляем zsh-специфичные настройки
    cat > "$zsh_script" << 'EOF'
# Zsh completion script for imgctl
# Generated from bash completion script

autoload -U compinit
compinit

EOF
    echo "$zsh_content" >> "$zsh_script"
    
    chmod +x "$zsh_script"
    echo "✓ Zsh completion создан: $zsh_script"
}

# Регистрируем completion
complete -F _imgctl_completion imgctl

# Если скрипт запущен напрямую, показываем меню управления
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    case "${1:-}" in
        install)
            _imgctl_completion_install "${@:2}"
            ;;
        test)
            _imgctl_completion_test
            ;;
        uninstall)
            _imgctl_completion_uninstall
            ;;
        *)
            _imgctl_completion_help
            ;;
    esac
fi

# Функция для обработки команды completion из imgctl
_imgctl_completion_command() {
    case "${1:-}" in
        install)
            _imgctl_completion_install "${@:2}"
            ;;
        test)
            _imgctl_completion_test
            ;;
        uninstall)
            _imgctl_completion_uninstall
            ;;
        *)
            _imgctl_completion_help
            ;;
    esac
}