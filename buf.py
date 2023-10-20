def numeral_paragraphs(self, elem):
        paragraph = elem[0].split('.')
        reletives = [elem[0]]
        delimetrs = [elem[4]]
        delimetr = elem[4]
        parent = None
        idx = elem[2] - len(elem[0]) - len(elem[4])
        # Поиск отсутствующих параграфов
        for i in range(2):
            p = None
            for i in range(-1, max(-len(self.tree), -40), -1):
                if self.tree[i].data_type == 'numbers': 
                    node = self.tree[i].node_name.split('.')
                    # Параграфы братья
                    if node[:-1] == paragraph[:-1]:
                        if int(node[-1]) >= int(paragraph[-1]):
                            p = self.tree[i].parent
                            continue
                        if p != self.tree[i].parent:
                            parent, delimetr = self.tree[i].parent, self.tree[i].delimetr
                            break
                    # node это отец текущего параграфа
                    elif node == paragraph[:-1]:
                        parent, delimetr = self.tree[i], self.tree[i].delimetr[:-1]
                        break
            if parent:
                break
            delimetr = delimetr[:-1]
            paragraph = paragraph[:-1]
            reletives.append(paragraph)
            delimetrs.append('\n' + delimetr)
        else:
            if len(elem[0].split('.')) == 2:
                sp = list(map(int, elem[0].split('.')))
                if find(self.root, lambda node: node.path_name == "/txt/{}.{}".format(sp[0], sp[1])):
                    st = False
                    for i in range(k+1, min(len(lst), k+21)):
                        if self.param and self.tree:
                            if 'numbers' not in lst[i][3]:
                                continue
                            if self.numeral_check(elem[0], lst[i][0]):
                                st = True
                            if self.numeral_check(self.param.node_name, lst[i][0]):
                                if st:
                                    parent=self.tree[-1]
                                    if sp[0] == 2:
                                        self.tree.append(Node('{}.'.format(1), sign=elem[1], pos=elem[2], parent=parent, data_type='number', status='MISSING', delimetr = elem[4]))
                                    for j in range(1, sp[1]):
                                        self.tree.append(Node('{}.{}'.format(sp[0], j), sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='MISSING', delimetr = elem[4]))
                                    self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING', delimetr = elem[4]))
                                    self.param = self.tree[-1]
                                break
                        else:
                            parent=self.root
                            if sp[0] == 2:
                                self.tree.append(Node('{}.'.format(1), sign=elem[1], pos=elem[2], parent=parent, data_type='number', status='MISSING', delimetr = elem[4]))
                            for j in range(1, sp[1]):
                                self.tree.append(Node('{}.{}'.format(sp[0], j), sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='MISSING', delimetr = elem[4]))
                            self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING', delimetr = elem[4]))
                            self.param = self.tree[-1]
                            break

                    else:
                        self.trees.append(tree_to_dict(self.root, all_attrs=True))
                        del self.tree
                        del self.root
                        self.root = Node("txt")
                        self.tree = []
                        parent=self.root
                        if sp[0] == 2:
                            self.tree.append(Node('{}.'.format(1), sign=elem[1], pos=elem[2], parent=parent, data_type='number', status='MISSING', delimetr = elem[4]))
                        for j in range(1, sp[1]):
                            self.tree.append(Node('{}.{}'.format(sp[0], j), sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='MISSING', delimetr = elem[4]))
                        self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING', delimetr = elem[4]))
                        self.param = self.tree[-1]
                        self.param = self.tree[-1]

                # if find(self.root, lambda node: node.path_name == "/txt/{}.{}".format(sp[0], int(sp[1])-1)) or sp[1] == 1:
                #     # self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=self.root, data_type=elem[3], status='EXISTING', delimetr = elem[4]))
                #     if int(sp[1]) < 3:
                #         for i in range(1, sp[1]):
                #             self.tree.append(Node('.'.join([sp[0], str(i)]), sign=elem[1], pos=elem[2], parent=self.root, data_type=elem[3], status='EXISTING', delimetr = elem[4]))
                #     self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=self.root, data_type=elem[3], status='EXISTING', delimetr = elem[4]))
                #     self.param = self.tree[-1]
            return

        # Восстановка отсутствующих параграфов
        buf = []
        for i in range(-1, -len(reletives), -1):
            start, end = 0, int(reletives[i][-1])
            for j in range(len(self.tree)):
                if self.tree[j].node_name.split('.')[:-1] == reletives[i][:-1]:
                    start = int(self.tree[j].node_name.split('.')[-1])
            if (end - start - 1) > 3:
                return
            for k in range(start+1, end):
                self.tree.append(Node('.'.join(reletives[i][:-1]+[str(k)]), sign='.', pos=idx, parent=parent, data_type='numbers', status='MISSING', delimetr = delimetr))
            self.tree.append(Node('.'.join(reletives[i]), sign='.', pos=idx, parent=parent, data_type='numbers', status='MISSING', delimetr = delimetr))               
            parent = self.tree[-1]
            delimetr = delimetrs[i]
        # Выравниваем предупреждения по форме предыдущих параграфов
        for i in range(-1, -len(self.tree)-1, -1):
            if self.tree[i].node_name.split('.')[:-1] == elem[0].split('.')[:-1]:
                if self.tree[i].status == 'MISSING':
                    self.tree[i].delimetr = elem[4]
        # Конец проверки
        
        # работаем над параграфом, который нашли и смотрим, каких частей до него не хватает
        end = int(elem[0].split('.')[-1])
        start = 0
        for j in range(len(self.tree)):
            if self.tree[j].node_name.split('.')[:-1] == elem[0].split('.')[:-1]:
                start = int(self.tree[j].node_name.split('.')[-1])
        for k in range(start+1, end):
            self.tree.append(Node('.'.join(elem[0].split('.')[:-1]+[str(k)]), sign='.', pos=idx, parent=parent, data_type='numbers', status='MISSING', delimetr = elem[4]))

        self.tree.append(Node(elem[0], sign=elem[1], pos=elem[2], parent=parent, data_type=elem[3], status='EXISTING', delimetr = elem[4]))
        self.param = self.tree[-1]