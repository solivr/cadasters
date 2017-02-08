import datetime
import numpy as np
# from text import print_digit_counts
# import text


def write_log_file(filename, **kwargs):

    cadaster_filename = kwargs.get('cadaster_filename', None)
    size_image = kwargs.get('size_image', None)
    params_slic = kwargs.get('params_slic', None)
    list_dict_features = kwargs.get('list_dict_features', None)
    similarity_method = kwargs.get('similarity_method', None)
    stop_criterion = kwargs.get('stop_criterion', None)
    elapsed_time = kwargs.get('elapsed_time', None)
    classifier_filename = kwargs.get('classifier_filename', None)
    iou_thresh_parcels = kwargs.get('iou_thresh_parcels', None)
    # correct_poly = kwargs.get('correct_poly', None)
    # incorrect_poly = kwargs.get('incorrect_poly', None)
    # total_poly = kwargs.get('total_poly', None)
    results_eval_parcels = kwargs.get('results_eval_parcels', None)
    iou_thresh_digits = kwargs.get('iou_thresh_digits', None)
    # true_positive_numbers = kwargs.get('true_positive_numbers', None)
    # false_positive_numbers = kwargs.get('false_positive_numbers', None)
    # missed_numbers = kwargs.get('missed_numbers', None)
    # total_predicted_numbers = kwargs.get('total_predicted_numbers', None)
    results_eval_digits = kwargs.get('results_eval_digits', None)
    CER = kwargs.get('CER', None)
    counts_digits = kwargs.get('counts_digits', None)

    minutes, seconds = divmod(np.float32(elapsed_time), 60)
    hours, minutes = divmod(minutes, 60)
    date = datetime.datetime.now()

    # Open file (or create it)
    log_file = open(filename, 'w+')
    log_file.write('Date of log creation : {:02d}.{:02d}.{:02d} at {:02d}:{:02d} \n'
                   .format(date.day, date.month, date.year, date.hour, date.minute))
    log_file.write('Time elapsed to process image : {:02d}:{:02d}:{:02d}\n\n'
                   .format(int(hours), int(minutes), int(seconds)))

    log_file.write('---- Image  -----\n')
    log_file.write('Filename : {}'.format(cadaster_filename))
    log_file.write(', size : {}x{} \n'.format(size_image[0], size_image[1]))
    log_file.write('---- Superpixels ----\n')
    log_file.write(' Params : {}\n'.format(params_slic))
    log_file.write('---- Features ----\n')
    log_file.write('{} \n'.format(list_dict_features))
    log_file.write(' ---- Merging ---- \n')
    log_file.write('Similarity method : {}\n'.format(similarity_method))
    log_file.write('Stop criterion : {}\n'.format(stop_criterion))
    log_file.write('---- Classification ----\n')
    log_file.write('Classifier file: {}\n'.format(classifier_filename))

    if results_eval_parcels:
        log_file.write('---- Evaluation parcels ----\n')
        log_file.write('IoU threshold : {}\n'.format(iou_thresh_parcels))
        log_file.write('Total parcels (groundtruth) : {}\n'.format(results_eval_parcels['total_groundtruth']))
        log_file.write('Total extracted parcels : {}\n'.format(results_eval_parcels['total_extracted']))
        log_file.write('True positives parcels : {}/{}  /  Precision : {:.02f}\n'.format(
            results_eval_parcels['true_positive'], results_eval_parcels['total_groundtruth'],
            results_eval_parcels['precision']))
        log_file.write('False positives parcels : {}/{}  /  Recall : {:.02f}\n'.format(
            results_eval_parcels['false_positive'], results_eval_parcels['total_extracted'],
            results_eval_parcels['recall']))
        # log_file.write('Precision : {:.02f}\n'.format(results_eval_parcels['precision']))
        # log_file.write('Recall : {:.02f}\n'.format(results_eval_parcels['recall']))

    if results_eval_digits:

        log_file.write('---- Evaluation digits ----\n')

        log_file.write('** Localization\n')
        log_file.write('IoU threshold : {}\n'.format(iou_thresh_digits))
        log_file.write('Total labels (groundtruth) : {}\n'.format(results_eval_digits['total_groundtruth']))
        log_file.write('Total extracted boxes : {}\n'.format(results_eval_digits['total_predicted']))
        log_file.write('True positive boxes : {}/{}\n'.format(results_eval_digits['true_positive_box'],
                                                              results_eval_digits['total_groundtruth']))
        log_file.write('False positive boxes : {}/{}\n'.format(results_eval_digits['false_positive_box'],
                                                               results_eval_digits['total_predicted']))

        log_file.write('** Recognition\n')
        log_file.write('Correct recognized numbers : {}/{} ({:.02f}) \n'.format(results_eval_digits['true_positive_numbers'],
                                                                      results_eval_digits['true_positive_box'],
                                results_eval_digits['true_positive_numbers'] / results_eval_digits['true_positive_box']))
        # log_file.write('Missed (Non-extracted) numbers : {}/{} ({:.02f})\n'.format(missed_numbers, total_true_numbers,
        #                                                                         missed_numbers / total_true_numbers))
    if (CER is not None) and (counts_digits is not None):
        log_file.write('Character Error Rate (CER) : {:.02f}\n'.format(CER))

        n_partial_numbers = sum(np.array([counts_digits[i] for i in counts_digits.keys()]))
        log_file.write('Partial retrieval {}/{} (:.02f)\n'.format(n_partial_numbers,
                                                                  results_eval_digits['total_groundtruth'],
                                                        n_partial_numbers / results_eval_digits['total_groundtruth']))
        log_file.write(print_digit_counts(counts_digits))

    # Close file
    log_file.close()


def print_digit_counts(counts_digits):

    total_counts = sum(np.array([counts_digits[i] for i in counts_digits.keys()]))
    str_to_print = ''
    for i in sorted(counts_digits.keys(), reverse=True):
        str_to_print += '\t{} digit(s) : {}/{} ({:.02f})\n'.format(i, counts_digits[i], total_counts,
                                                                   counts_digits[i] / total_counts)
    return str_to_print
