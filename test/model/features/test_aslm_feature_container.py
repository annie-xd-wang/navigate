"""Copyright (c) 2021-2022  The University of Texas Southwestern Medical Center.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted for academic and research use only (subject to the limitations in the disclaimer below)
provided that the following conditions are met:

     * Redistributions of source code must retain the above copyright notice,
     this list of conditions and the following disclaimer.

     * Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions and the following disclaimer in the
     documentation and/or other materials provided with the distribution.

     * Neither the name of the copyright holders nor the names of its
     contributors may be used to endorse or promote products derived from this
     software without specific prior written permission.

NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY
THIS LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""
import unittest
import random

from aslm.model.features.feature_container import SignalNode, DataNode, DataContainer, load_features
from aslm.model.features.common_features import WaitToContinue
from aslm.model.features.feature_container import dummy_True
from aslm.model.dummy import DummyFeature, DummyModel

def generate_random_feature_list(has_response_func=False, multi_step=False, with_data_func=True):
    feature_list = []
    m = random.randint(1, 10)
    node_count = 0
    for i in range(m):
        n = random.randint(1, 10)
        temp = []
        for j in range(n):
            has_response = random.randint(0, 1) if has_response_func else 0
            device_related = random.randint(0, 1)
            steps = random.randint(1, 10) if multi_step else 1
            steps = 1 if steps < 5 else steps
            if with_data_func == False:
                no_data_func = random.randint(0, 1)
            else:
                no_data_func = 0
            if steps >= 5 and no_data_func:
                has_response = False
                feature = {'name': DummyFeature, 'args': (f'multi-step{node_count}', has_response, 1, steps, False, )}
                temp.append(feature)
                temp.append({'name': WaitToContinue})
            else:
                feature = {'name': DummyFeature, 'args': (f'node{node_count}', has_response, device_related, steps,)}
                if has_response:
                    feature['node'] = {'need_response': True}
                temp.append(feature)
            node_count += 1
            # has response function means that node can only have child node
            if has_response:
                break
        feature_list.append(temp)
    return feature_list

def print_feature_list(feature_list):
    result = []
    for features in feature_list:
        temp = []
        for node in features:
            if 'args' in node:
                temp.append(node['args'])
            else:
                temp.append((node['name'].__name__))
        result.append(temp)
    print('--------feature list-------------')
    print(result)
    print('---------------------------------')
    return str(result)

def convert_to_feature_list(feature_str):
    result = []
    for features in feature_str:
        temp = []
        for feature in features:
            if type(feature) == str:
                node = {'name': WaitToContinue}
            else:
                node = {'name': DummyFeature, 'args': (*feature,)}
            temp.append(node)
        result.append(temp)
    return result


class TestFeatureContainer(unittest.TestCase):

    def setUp(self):
        print('-------------new test case-----------------')

    @unittest.skip('takes long time to finish the test')
    def test_feature_container(self):
        model = DummyModel()
        print('# test signal and data are synchronous')
        print('--all function nodes are single step')
        
        print('----all signal nodes are without waiting function')
        for i in range(10):
            feature_list = generate_random_feature_list()
            model.start(feature_list)
            print(model.signal_records)
            print(model.data_records)
            assert model.signal_records == model.data_records, print_feature_list(feature_list)

        print('----some signal nodes have waiting function')
        for i in range(10):
            feature_list = generate_random_feature_list(has_response_func=True)
            print_feature_list(feature_list)
            model.start(feature_list)
            print(model.signal_records)
            print(model.data_records)
            assert model.signal_records == model.data_records, print_feature_list(feature_list)

        print('--Some function nodes are multi-step')
        print('----multi-step nodes have both signal and data functions, and without waiting function')
        for i in range(10):
            feature_list = generate_random_feature_list(multi_step=True)
            # feature_list = convert_to_feature_list([[('node0', 0, 1, 2), ('node1', 0, 0, 3)]])
            # feature_list = convert_to_feature_list([[('node0', 0, 0, 5)], [('node1', 0, 0, 5), ('node2', 0, 0, 10), ('node3', 0, 1, 7), ('node4', 0, 0, 1), ('node5', 0, 0, 9), ('node6', 0, 1, 9)], [('node7', 0, 0, 9), ('node8', 0, 0, 6), ('node9', 0, 0, 7), ('node10', 0, 1, 3), ('node11', 0, 1, 6), ('node12', 0, 1, 5), ('node13', 0, 0, 4), ('node14', 0, 0, 1), ('node15', 0, 0, 2)], [('node16', 0, 0, 5), ('node17', 0, 1, 2), ('node18', 0, 0, 6), ('node19', 0, 0, 3)], [('node20', 0, 0, 9), ('node21', 0, 0, 7), ('node22', 0, 0, 1), ('node23', 0, 0, 8), ('node24', 0, 0, 2), ('node25', 0, 1, 7), ('node26', 0, 0, 9)], [('node27', 0, 0, 2), ('node28', 0, 1, 3), ('node29', 0, 0, 3), ('node30', 0, 0, 8)], [('node31', 0, 0, 8), ('node32', 0, 0, 10), ('node33', 0, 1, 4), ('node34', 0, 1, 2), ('node35', 0, 1, 8), ('node36', 0, 1, 4), ('node37', 0, 0, 5), ('node38', 0, 0, 9)], [('node39', 0, 0, 9), ('node40', 0, 1, 8), ('node41', 0, 1, 4)], [('node42', 0, 0, 1), ('node43', 0, 0, 1), ('node44', 0, 1, 1), ('node45', 0, 0, 2), ('node46', 0, 1, 3)]])
            print_feature_list(feature_list)
            model.start(feature_list)
            print(model.signal_records)
            print(model.data_records)
            assert model.signal_records == model.data_records, print_feature_list(feature_list)

        print('----multi-step nodes have both signal and data functions, and with waiting function')
        for i in range(10):
            feature_list = generate_random_feature_list(has_response_func=True, multi_step=True)            
            print_feature_list(feature_list)
            model.start(feature_list)
            print(model.signal_records)
            print(model.data_records)
            assert model.signal_records == model.data_records, print_feature_list(feature_list)

        print("----some multi-step nodes don't have data functions")
        for i in range(10):
            # feature_list = convert_to_feature_list([[('node0', 0, 1, 1), ('multi-step1', False, 0, 6, False), 'WaitToContinue', ('multi-step2', False, 0, 8, False), 'WaitToContinue', ('node3', 0, 1, 1), ('multi-step4', False, 0, 9, False), 'WaitToContinue'], [('node5', 0, 0, 6)]])
            # feature_list = convert_to_feature_list([[('node0', 1, 1, 1)], [('node1', 0, 1, 9), ('node2', 0, 1, 1), ('node3', 0, 0, 1), ('multi-step4', False, 0, 9, False), 'WaitToContinue', ('multi-step5', False, 0, 5, False), 'WaitToContinue', ('node6', 1, 1, 1)]])
            feature_list = generate_random_feature_list(has_response_func=True, multi_step=True, with_data_func=False)            
            print_feature_list(feature_list)
            model.start(feature_list)
            print(model.signal_records)
            print(model.data_records)
            assert model.signal_records == model.data_records, print_feature_list(feature_list)

    def test_load_feature(self):
        def check(tnode1, tnode2):
            if tnode1 is None and tnode2 is None:
                return True
            if tnode1 is None or tnode2 is None:
                return False
            return tnode1.node_funcs['name-for-test'] == tnode2.node_funcs['name-for-test']

        def is_isomorphic(tree1, tree2):
            p, q = tree1, tree2
            stack = []
            while p or q or stack:
                if not check(p, q):
                    return False
                if p:
                    stack.append((p.sibling, q.sibling))
                    p, q = p.child, q.child
                else:
                    p, q = stack.pop()
            return True

        # generates 10 random feature lists and verify whether they are loaded correctly
        for i in range(10):
            feature_list = generate_random_feature_list()
            signal_container, data_container = load_features(self, feature_list)
            assert is_isomorphic(signal_container.root, data_container.root)
            print('-', i, 'random feature list is correct!')       

    def test_signal_node(self):
        feature = DummyFeature()
        func_dict = {
            'init': feature.init_func,
            'main': feature.main_func,
            'end': feature.end_func
        }

        print('without waiting for a response:')
        node = SignalNode('test_1', func_dict)
        assert node.need_response == False
        assert node.node_funcs['end']() == False

        feature.is_end = True
        assert node.node_funcs['end']() == True

        result, is_end = node.run()
        assert feature.init_times == 1
        assert feature.running_times_main_func == 1
        assert result == None
        assert is_end == True
        assert node.is_initialized == False

        result, is_end = node.run(True)
        assert feature.init_times == 2
        assert feature.running_times_main_func == 2
        assert result == True
        assert is_end == True
        assert node.is_initialized == False
        assert node.wait_response == False

        print('--running with waiting option')
        feature.clear()
        result, is_end = node.run(wait_response=True)
        assert is_end == True
        assert node.is_initialized == False
        assert node.wait_response == False
        assert feature.running_times_main_func == 1
        assert feature.init_times == 1

        print('--device related')
        feature.clear()
        node = SignalNode('test_1', func_dict, device_related=True)
        print(node.node_type)
        assert node.need_response == False
        result, is_end = node.run()
        assert is_end == True
        assert node.wait_response == False
        assert feature.running_times_main_func == 1

        print('----running with waitint option')
        feature.clear()
        result, is_end = node.run(wait_response=True)
        assert is_end == False
        assert node.wait_response == False
        assert feature.running_times_main_func == 0
        assert node.is_initialized == True

        print('----multi-step function')
        feature.clear()
        node.node_type = 'multi-step'
        assert func_dict.get('main-response', None) == None
        assert node.need_response == False
        steps = 5
        for i in range(steps+1):
            feature.is_end = (i == steps)
            result, is_end = node.run()
            if i < steps:
                assert node.is_initialized == True
                assert is_end == False
            else:
                assert node.is_initialized == False
                assert is_end == True
            assert feature.running_times_main_func == i+1
            assert node.wait_response == False
            if i < steps:
                result, is_end = node.run(wait_response=True)
                assert is_end == False

        print('--multi-step function')
        feature.clear()
        node = SignalNode('test_1', func_dict, node_type='multi-step', device_related=True)
        assert func_dict.get('main-response') == None
        assert node.need_response == False
        assert node.device_related == True
        steps = 5
        for i in range(steps+1):
            feature.is_end = (i == steps)
            result, is_end = node.run()
            if i < steps:
                assert is_end == False
            else:
                assert is_end == True
                break
            assert is_end == False
            assert feature.running_times_main_func == i+1
            assert node.is_initialized == True
            assert node.wait_response == False
            result, is_end = node.run(wait_response=True)
        assert node.wait_response == False
        assert node.is_initialized == False

        print('wait for a response:')
        feature.clear()
        func_dict['main-response'] = feature.response_func
        node = SignalNode('test_2', func_dict, need_response=True)
        assert node.need_response == True
        assert node.wait_response == False

        print('--running without waiting option')
        result, is_end = node.run()
        assert result == None
        assert is_end == False
        assert node.is_initialized == True
        assert node.wait_response == True

        result, is_end = node.run(True)
        assert result == True
        assert is_end == False
        assert feature.init_times == 1
        assert feature.running_times_main_func == 2
        assert node.wait_response == True
        assert node.is_initialized == True

        print('--running with waiting option')
        result, is_end = node.run(wait_response=True)
        assert feature.running_times_main_func == 2
        assert feature.running_times_response_func == 1
        assert node.wait_response == False
        assert node.is_initialized == False
        assert is_end == True

        feature.clear()
        result, is_end = node.run(wait_response=True)
        assert is_end == False
        assert feature.init_times == 1
        assert feature.running_times_main_func == 0
        assert feature.running_times_response_func == 0
        assert node.is_initialized == True

        print('----device related')
        node.device_related = True
        feature.clear()
        result, is_end = node.run()
        assert is_end == False
        assert feature.running_times_main_func == 1
        assert node.wait_response == True
        assert node.is_initialized == True

        result, is_end = node.run(wait_response=True)
        assert is_end == True
        assert feature.running_times_response_func == 1
        assert feature.running_times_main_func == 1
        assert node.wait_response == False
        assert node.is_initialized == False

        feature.clear()
        result, is_end = node.run(wait_response=True)
        assert is_end == False
        assert feature.running_times_main_func == 0
        assert node.wait_response == False
        assert feature.init_times == 1
        assert node.is_initialized == True

        print('--multi-step function')
        feature.clear()
        node = SignalNode('test', func_dict, node_type='multi-step', need_response=True)
        steps = 5
        for i in range(steps+1):
            feature.is_end = (i == steps)
            result, is_end = node.run()
            assert is_end == False
            assert feature.running_times_main_func == i+1
            assert node.is_initialized == True
            result, is_end = node.run(wait_response=True)
            if i < steps:
                assert is_end == False
            else:
                assert is_end == True
            assert feature.running_times_response_func == i+1
            assert node.wait_response == False

    def test_node_cleanup(self):
        def wrap_error_func(func):
            def temp_func(raise_error=False):
                if raise_error:
                    raise Exception
                func()
            return temp_func

        feature = DummyFeature()
        func_dict = {
            'init': feature.init_func,
            'pre-main': dummy_True,
            'main': wrap_error_func(feature.main_func),
            'end': feature.end_func,
        }
        # one-step node without response
        print('- one-step node without response')
        node = DataNode('cleanup_node', func_dict)
        data_container = DataContainer(node)
        assert data_container.root == node
        data_container.run()
        assert feature.running_times_main_func == 1, feature.running_times_main_func
        data_container.run(True)
        assert node.is_marked == True
        assert feature.running_times_main_func == 1, feature.running_times_main_func

        feature.clear()
        func_dict['cleanup'] = feature.close
        node = DataNode('cleanup_node', func_dict)
        data_container = DataContainer(node)
        data_container.run()
        data_container.run(True)
        assert feature.is_closed == True
        assert node.is_marked == True
        assert feature.running_times_main_func == 1
        data_container.run()
        assert feature.running_times_main_func == 1

        # node with response
        print('- node with response')
        feature.clear()
        node = DataNode('cleanup_node', func_dict, need_response=True)
        data_container = DataContainer(node, [node])
        assert data_container.root == node
        data_container.run()
        assert feature.running_times_main_func == 1, feature.running_times_main_func
        data_container.run(True)
        assert feature.running_times_cleanup_func == 1
        assert feature.is_closed == True
        assert node.is_marked == False
        assert feature.running_times_main_func == 1
        assert data_container.end_flag == True
        data_container.run()
        assert feature.running_times_main_func == 1

        # multiple nodes
        print('- multiple nodes')
        feature.clear()
        node1 = DataNode('cleanup_node1', func_dict)
        node2 = DataNode('cleanup_node2', func_dict, device_related=True)
        node3 = DataNode('cleanup_node3', func_dict, need_response=True, device_related=True)
        node1.sibling = node2
        node2.sibling = node3
        cleanup_list = [node1, node2, node3]
        data_container = DataContainer(node1, cleanup_list)
        assert data_container.root == node1
        assert feature.running_times_main_func == 0

        for i in range(1, 4):
            data_container.run()
            assert feature.running_times_main_func == i, feature.running_times_main_func
        # mark a single node
        data_container.run(True)
        assert feature.is_closed == True
        assert feature.running_times_cleanup_func == 1
        feature.is_closed = False
        assert node1.is_marked == True
        assert feature.running_times_main_func == 3
        assert data_container.end_flag == False
        data_container.run()
        assert feature.running_times_main_func == 4
        assert node2.is_marked == False
        data_container.run()
        assert feature.running_times_main_func == 5
        assert node3.is_marked == False
        # run node1 which is marked
        data_container.run()
        assert feature.running_times_main_func == 5
        # run node2
        data_container.run()
        assert feature.running_times_main_func == 6
        assert node2.is_marked == False
        # run node3 and clean up all nodes
        data_container.run(True)
        assert feature.running_times_cleanup_func == 4
        assert feature.running_times_main_func == 6
        assert data_container.end_flag == True


if __name__ == '__main__':
    unittest.main()